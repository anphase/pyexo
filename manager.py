from __future__ import unicode_literals

import requests

try:
    from vumeda_api.settings import EXO_URL
except ImportError:
    from .settings import EXO_URL
try:
    from basemanager import BaseManager
except ImportError:
    from .basemanager import BaseManager
try:
    from utils import isplural, singular
except ImportError:
    from .utils import isplural, singular


class Manager(BaseManager):
    def __init__(self, name, credentials, user_agent=None):
        from . import __version__ as VERSION
        self.credentials = credentials
        self.base_url = EXO_URL
        self.extra_params = {"pagesize": "100"}

        if isplural(name):
            self.name = singular(name)
        else:
            self.name = name

        if user_agent is None:
            self.user_agent = 'pyexo/%s ' % VERSION + requests.utils.default_user_agent()
        else:
            self.user_agent = user_agent

        for method_name in self.DECORATED_METHODS:
            method = getattr(self, '_%s' % method_name)
            setattr(self, method_name, self._get_data(method))
