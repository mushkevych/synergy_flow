__author__ = 'Bohdan Mushkevych'

from synergy.db.dao.base_dao import BaseDao
from flow.db.model.flow import Flow, FLOW_NAME, TIMEPERIOD


COLLECTION_FLOW = 'flow'


class FlowDao(BaseDao):
    """ Thread-safe Data Access Object for *flow* table/collection """

    def __init__(self, logger):
        super(FlowDao, self).__init__(logger=logger,
                                      model_class=Flow,
                                      primary_key=[FLOW_NAME, TIMEPERIOD],
                                      collection_name=COLLECTION_FLOW)
