import concurrent.futures
from fastapi import FastAPI
from pydantic import BaseModel
from requests import *
import uvicorn
import os
import logging

# Custom functions
from resourses.ds_functions import DSServices

# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Dict storage for messages. For now it is a simple dict.
storage = {}
# Secondary urls
secondaries = {
    'http://localhost:8001/append',
    'http://localhost:8002/append',
}
secondariesStatus = {}

# Message class description
class MSG(BaseModel):
    id: int
    msg: str

# Init FastAPI
app = FastAPI()

# Routes
@app.get('/list')
async def get_msgs_list():
    return DSServices.get_msgs(storage)

# Health status
@app.get('/health')
async def get_health_status(request: Request):
    # 
    # Check response status code by own url.
    response_code = DSServices.get_healts_code(str(Request.url))
    health_status = 'Unhealthy'
    # Active
    if response_code == 200:
        health_status = 'Healthy'
    # Busy    
    elif response_code == 204:
        health_status = 'Healthy'

    return health_status

@app.post('/append')
async def set_msg(msg: MSG, write_concern: int = 1):
    logger.info(os.getenv('APP_LEVEL'))
    # Master part
    if os.getenv('APP_LEVEL') == 'master':        
        # Replicate to secondaries
        if (write_concern > 1):
            allGood = True
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = []
                for url in secondaries:
                    results.append(executor.submit(DSServices.postRequest, url=url, data=msg))
                for future in concurrent.futures.as_completed(results):
                    try:
                        logger.info(future.result())
                    except RequestException as e:
                        allGood = False
                        logger.info(e)

            # All messages should be appended.
            # Count of appended messages must follw wtite concern rules.
            if not allGood and ((len(results) - 1) != write_concern):
                return 'Something went wrong! Please check logs.'        

    # Save on master
    masterResponse = DSServices.post_msg(msg, storage)
       
    # Secondaries part
    secondaryResponses = []
    if os.getenv('APP_LEVEL') == 'secondary':
        secondaryResponses.append(DSServices.post_msg(msg, storage))
    
    if 'REJECTED' in secondaryResponses:
        return 'Something went wrong! Please check logs.'

    return 'MSG appended' 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT')))
    # Start heartbeater
    DSServices.heartbeat_it(secondaries, secondariesStatus)
    # Remove Test 
    #uvicorn.run(app, host="0.0.0.0", port=int(5007))
