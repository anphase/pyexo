import base64
try:
    from vumeda_api.settings import (EXO_USERNAME,
                                     EXO_PASSWORD,
                                     EXO_API_KEY,
                                     EXO_TOKEN)
except ImportError:
    from .settings import (EXO_USERNAME,
                           EXO_PASSWORD,
                           EXO_API_KEY,
                           EXO_TOKEN)


class Credentials(object):
    def __init__(self, username=EXO_USERNAME, password=EXO_PASSWORD,
                 key=EXO_API_KEY, token=EXO_TOKEN):
        self._username = username
        self._password = password
        self._key = key
        self._token = token

        self.auth_headers = {
            'Authorization': self._basic_auth_code(self._username, self._password),
            'x-myobapi-key': self._key,
            'x-myobapi-exotoken': self._token,
        }

    @staticmethod
    def _basic_auth_code(username, password):
        auth_data = '{}:{}'.format(username, password)
        return "Basic " + str(base64.b64encode(auth_data.encode()))
