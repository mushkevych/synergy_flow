__author__ = 'Bohdan Mushkevych'

import pymongo
from synergy.db.manager import ds_manager
from synergy.scheduler.scheduler_constants import PROCESS_SCHEDULER
from synergy.system.system_logger import get_logger

from flow.db.model.flow import FLOW_NAME, TIMEPERIOD
from flow.db.model.step import STEP_NAME
from flow.flow_constants import COLLECTION_FLOW, COLLECTION_STEP


def reset_db():
    """ drops *synergy.flow* tables and re-creates them """
    logger = get_logger(PROCESS_SCHEDULER)
    logger.info('Starting *synergy.flow* tables reset')

    ds = ds_manager.ds_factory(logger)
    ds._db.drop_collection(COLLECTION_STEP)
    ds._db.drop_collection(COLLECTION_FLOW)

    connection = ds.connection(COLLECTION_STEP)
    connection.create_index([(FLOW_NAME, pymongo.ASCENDING),
                             (STEP_NAME, pymongo.ASCENDING),
                             (TIMEPERIOD, pymongo.ASCENDING)], unique=True)

    connection = ds.connection(COLLECTION_FLOW)
    connection.create_index([(FLOW_NAME, pymongo.ASCENDING),
                             (TIMEPERIOD, pymongo.ASCENDING)], unique=True)

    logger.info('*synergy.flow* tables have been recreated')


if __name__ == '__main__':
    pass
