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
    def get_single_msg(id: int, storage: dict):
        return {storage[id]}

    def get_msgs(storage: dict):
        logger.info('Get messages list')

        return storage

    """
    msg: Messege
    storage: array (memory) for a starage
    w: write convcern (Optional, used in calls to seconderies)
    """
    def post_msg(msg: str, storage: dict):
        try:
            # Set timeouts
            logger.info('Sleeping for a 4')
            time.sleep(4)
            # Set message
            storage[msg.id] = msg.msg
            # Log message store event
            logger.info(msg.id)

            return 'ACK'
        except:
            logger.error('An error happened while put message operation')
            return 'REJECTED'

    def postRequest(url, data):
        response = requests.post(url, [], timeout=10)
        return response.status_code


    def get_write_concern(write_concern: int = None):
        return write_concern


    def get_healts_code(url):
        try:
            response = requests.get(url)
            return response.status_code
        except:
            logger.error('Could not get server health status')
            return 0
    
    def set_health_status(secondariesStatus: dict, current_status: str, secondary_url: str):
        secondariesStatus[secondary_url] = current_status

    def heartbeat_it(self, urls: dict, secondariesStatus: dict):
        for i in range(10):
            try:
                time.sleep(0.5)
                for url in urls:
                    DSServices.set_health_status(secondariesStatus, self.get_healts_code(url), url)

                
                break
            except Exception:
                logger.error('Could not get server health status')
                continue

