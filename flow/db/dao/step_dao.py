__author__ = 'Bohdan Mushkevych'

from bson.objectid import ObjectId
from synergy.system.decorator import thread_safe

from synergy.db.dao.base_dao import BaseDao
from flow.db.model.step import Step, FLOW_NAME, STEP_NAME, TIMEPERIOD, RELATED_FLOW

COLLECTION_STEP = 'step'


class StepDao(BaseDao):
    """ Thread-safe Data Access Object for *step* table/collection """

    def __init__(self, logger):
        super(StepDao, self).__init__(logger=logger,
                                      model_class=Step,
                                      primary_key=[FLOW_NAME, STEP_NAME, TIMEPERIOD],
                                      collection_name=COLLECTION_STEP)

    @thread_safe
    def remove_by_flow_id(self, flow_id):
        """ removes all steps for given flow_id """
        collection = self.ds.connection(COLLECTION_STEP)
        return collection.delete_many(filter={RELATED_FLOW: ObjectId(flow_id)})
