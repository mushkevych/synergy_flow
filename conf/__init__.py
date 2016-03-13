__author__ = 'Bohdan Mushkevych'

from synergy.conf import LazyProxy


ENVIRONMENT_FLOWS_VARIABLE = 'SYNERGY_FLOWS_MODULE'


flows = LazyProxy(ENVIRONMENT_FLOWS_VARIABLE, 'flows', {})
