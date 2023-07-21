"""
Set of custom functions
    Get MSGs List
    Set MSG
"""
import logging
import requests
import time

logger = logging.getLogger(__name__)

class DSServices:
    def __init__(self):
        pass

    def get_single_msg(id: int, storage: dict):
        return {storage[id]}

    def get_msgs(storage: dict):
        logger.info('Get messages list')

        return storage

    """
    msg: Message
    storage: In memory dict for a storage
    sleep: Seconds to sleep before store new message
    """
    def post_msg(msg: str, storage: dict, sleep: int = 0):
        try:
            # Set timeouts
            logger.info('Sleeping for a ' + str(sleep) + ' seconds')
            time.sleep(sleep)
            # Get message ID from storage
            id = DSServices.get_msg_id(storage)
            # Set message
            storage[id] = msg.msg
            # Log message store event
            logger.info('logged msg ID: ' + str(id))

            return 'ACK'
        except Exception as error:
            logger.error('An error happened while put message')
            logger.error(error)

            return 'REJECTED'

    def get_msg_id(storage: dict):
        return len(storage) + 1

    def postRequest(url, json):
        response = requests.post(url=url, data=json, timeout=5)
        return response.status_code


    def get_write_concern(write_concern: int = None):
        return write_concern


    def get_healts_code(url):
        #try:
            response = requests.get(url, timeout=5)
            return response.status_code
        #except:
        #    logger.info('Could not get server health status for URL: ' + str(url))
        #    return 0
    
    def set_health_status(secondariesStatus: dict, current_status: str, secondary_url: str):
        secondariesStatus[secondary_url] = current_status

    def heartbeat_it(urls: dict, secondariesStatus: dict):
        for i in range(10):
                logger.info(i)
            #try:
                time.sleep(0.5)
                for url in urls:
                    DSServices.set_health_status(secondariesStatus, DSServices.get_healts_code(url), url)
                
            #    break
            #except Exception:
            #    logger.info('Could not get server health status')
            #    continue

