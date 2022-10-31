from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
import sys
import logging

# Custom functions
from resourses.ds_functions import DSServices

# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Dict storage for messages. For now it is a simple dict.
storage = {}

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
    response = DSServices.post_msg(msg, storage)
    return response

if __name__ == "__main__":
    #uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT')))
    # Remove Test 
    uvicorn.run(app, host="0.0.0.0", port=int(5007))
