"""
Set of custom functions
    Get MSGs List
    Set MSG
"""
import time
import logging
logger = logging.getLogger(__name__)

class DSServices:
    def get_single_msg(id: int, storage: dict):
        return {storage[id]}

    def get_msgs(storage: dict):
        logger.info('Get messages list')

        return storage

    def post_msg(msg: str, storage: dict):
        try:
            # Set timeouts
            #logger.info('Sleeping for a 4')
            #time.sleep(4)
            # Set message
            storage[msg.id] = msg.msg
            # Log message store event
            logger.info(msg.id)

            return 'ACK'
        except:
            logger.error('An error happened while put message operation')
            return 'REJECTED'
