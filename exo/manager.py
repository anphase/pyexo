import requests

from .settings import EXO_URL
from .basemanager import BaseManager
from .utils import is_plural, singular


class Manager(BaseManager):
    def __init__(self, name, credentials, user_agent=None):
        from . import __version__ as VERSION
        self.credentials = credentials
        self.base_url = EXO_URL
        self.extra_params = {"pagesize": "100"}

        if is_plural(name):
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
