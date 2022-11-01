import concurrent.futures
from fastapi import FastAPI
from pydantic import BaseModel
from requests import RequestException
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

@app.post('/append')
async def set_msg(msg: MSG):
    logger.info(os.getenv('APP_LEVEL'))
    # Master part
    if os.getenv('APP_LEVEL') == 'master':
        # Save on master
        masterResponse = DSServices.post_msg(msg, storage)
        
        # Replicate to secondaries
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

        if not allGood:
            return 'Something went wrong! Please check logs.'            

       
    # Secondary part
    secondaryResponses = []
    if os.getenv('APP_LEVEL') == 'secondary':
        secondaryResponses.append(DSServices.post_msg(msg, storage))
    
    if 'REJECTED' in secondaryResponses:
        return 'Something went wrong! Please check logs.'

    return 'MSG appended' 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT')))
    # Remove Test 
    #uvicorn.run(app, host="0.0.0.0", port=int(5007))
