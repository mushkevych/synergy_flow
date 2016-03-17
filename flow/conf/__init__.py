__author__ = 'Bohdan Mushkevych'

import os
from synergy.conf import ImproperlyConfigured, LazyObject, Settings, empty

ENVIRONMENT_FLOWS_VARIABLE = 'SYNERGY_FLOWS_MODULE'


class LazyFlows(LazyObject):
    """ A lazy proxy for Synergy Flows """
    def _setup(self):
        """
        Load the flows definition module pointed to by the environment variable.
        This is used the first time we need any flows at all, if the user has not
        previously configured the flows manually.
        """
        settings_module = os.environ.get(ENVIRONMENT_FLOWS_VARIABLE, 'flows')
        if not settings_module:
            raise ImproperlyConfigured(
                'Requested flows module points to an empty variable. '
                'You must either define the environment variable {0} '
                'or call flows.configure() before accessing the settings.'
                .format(ENVIRONMENT_FLOWS_VARIABLE))

        self._wrapped = Settings(settings_module, default_settings={})

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup()
        return getattr(self._wrapped, name)


flows = LazyFlows()
