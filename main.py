import concurrent.futures
import json

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from requests import *
from starlette.requests import Request
import uvicorn
import os
import logging

# Custom functions
from resourses.ds_functions import DSServices

# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Dict storage for messages. For now, it is a simple dict.
storage = {}
# Secondary urls
secondaries = {
    'http://localhost:8001',
    'http://localhost:8002',
}
# sleep in seconds on secondaries
# url: seconds
secondaries_sleep = {
    'http://localhost:8001/append': 1,
    'http://localhost:8002/append': 3,
}
# secondaries responses
secondaries_responses = {}
secondariesStatus = {}

# Message class description
class MSG(BaseModel):
    msg: str
    write_concern: int

# Init FastAPI
app = FastAPI()

# Routes
@app.get('/list')
async def get_msgs_list():
    return DSServices.get_msgs(storage)

# Health status
@app.get('/health')
def get_health_status(request: Request):
    # health_status = secondariesStatus[str(request.url)]
    logger.info(secondariesStatus)
    return secondariesStatus
    health_status = secondariesStatus[str(request.url)]
    if (health_status is None):
        # Check response status code by own url.
        response_code = DSServices.get_healts_code(str(request.url))
        health_status = 'Unhealthy'
        # Active
        if response_code == 200:
            health_status = 'Healthy'
        # Busy    
        elif response_code == 204:
            health_status = 'Healthy'
        
        DSServices.set_health_status(secondariesStatus, health_status, str(request.url))

    return health_status

@app.post('/append')
async def set_msg(msg: MSG, background_tasks: BackgroundTasks, request: Request):
    master_response = ''
    logger.info('APP level: ' + os.getenv('APP_LEVEL'))

    # Master part
    if os.getenv('APP_LEVEL') == 'master':
        # Save on master
        master_response = DSServices.post_msg(msg, storage)

        # Replicate to secondaries
        allGood = True
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

            json_object = msg.model_dump_json()
            future_to_url = {executor.submit(DSServices.postRequest, url=url + '/append', json=json_object): url for url
                             in secondaries}

            #for future in concurrent.futures.wait(future_to_url, return_when='ALL_COMPLETED'):
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data == 200:
                        secondaries_responses[url] = 'ACK'
                    else:
                        secondaries_responses[url] = 'REJECTED'

                    # Check by write concern
                    if master_response == 'ACK':
                        # at lest one response is ACK
                       if msg.write_concern == 2 and secondaries_responses[url] == 'ACK':
                           return 'MSG appended for WC = 2'
                       elif msg.write_concern == 3 and len(secondaries_responses) == len(secondaries) and 'REJECTED' not in secondaries_responses:
                           return 'MSG appended for WC = 3'

                except Exception as exc:
                    logger.error('%r generated an exception: %s' % (url, exc))
       
    # Secondaries part
    #secondaryResponses = []
    if os.getenv('APP_LEVEL') == 'secondary':
        # we should not wait for replication, so it will be in background process
        if msg.write_concern == 1:
            background_tasks.add_task(DSServices.post_msg, msg, storage, sleep=secondaries_sleep[str(request.url)])
        # Replicate
        elif msg.write_concern > 1:
            DSServices.post_msg(msg, storage, sleep=secondaries_sleep[str(request.url)])

    #if 'REJECTED' in secondaryResponses:
    #    return 'Something went wrong! Please check logs.'

    # write_concern = 1, return to client
    if msg.write_concern == 1:
        if master_response == 'ACK':
            return 'MSG appended'
        else:
            return 'Something went wrong! Please check logs.'

    # General return
    return 'Something went wrong! Please check logs.'

if __name__ == "__main__":
    # Docker ports.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT')))
    # Test port
    #uvicorn.run(app, host="0.0.0.0", port=int(5007))
    # Start heartbeater
    # DSServices.heartbeat_it(urls=secondaries, secondariesStatus=secondariesStatus)
