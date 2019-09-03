from __future__ import unicode_literals


import json
import requests

try:
    from exceptions import (
        ExoBadRequest, ExoExceptionUnknown, ExoForbidden, ExoInternalError,
        ExoNotFound, ExoRemoved, ExoTimeout, ExoUnauthorised
    )
except ModuleNotFoundError:
    from .exceptions import (
        ExoBadRequest, ExoExceptionUnknown, ExoForbidden, ExoInternalError,
        ExoNotFound, ExoRemoved, ExoTimeout, ExoUnauthorised
    )
try:
    from utils import isplural, singular
except ModuleNotFoundError:
    from .utils import isplural, singular


class BaseManager(object):
    DECORATED_METHODS = (
        'all',
        'delete',
        'search',
        'get',
        'put',
        'save',
    )

    def _all(self, params=None):
        uri = '/'.join([self.base_url, self.name])
        uri_params = self.extra_params.copy()
        uri_params.update(params if params else {})
        return uri, uri_params, 'get', None, False

    def _delete(self, id):
        uri = '/'.join([self.base_url, self.name, id])
        return uri, {}, 'delete', None, False

    def _search(self, search_params, params=None):
        uri = '/'.join([self.base_url, self.name, 'search?q='+search_params])
        uri_params = self.extra_params.copy()
        uri_params.update(params if params else {})
        return uri, uri_params, 'get', None, True

    def _get(self, id, params=None):
        uri = '/'.join([self.base_url, self.name, id])
        uri_params = self.extra_params.copy()
        uri_params.update(params if params else {})
        return uri, uri_params, 'get', None, True

    def _put(self, data, validate=False):
        return self.save_or_put(data, validate, method='put')

    def _save(self, data, validate=False):
        return self.save_or_put(data, validate, method='post')

    def save_or_put(self, data, validate=False, method='post'):
        uri = '/'.join([self.base_url, self.name])
        if validate:
            uri = '/'.join([uri, 'validate'])
        params = self.extra_params.copy()
        return uri, params, method, data, False

    def _parse_api_response(self, response, resource_name):
        data = json.loads(response.text)
        try:
            return json.dumps(data, indent=4, sort_keys=True)  # [resource_name]
        except KeyError:
            return data

    def _get_data(self, func):
        """ This is the decorator for our DECORATED_METHODS.
        Each of the decorated methods must return:
            uri, params, method, body, headers, singleobject
        """
        def wrapper(*args, **kwargs):
            # timeout = kwargs.pop('timeout', None)
            timeout = 5

            uri, params, method, body, singleobject = func(*args, **kwargs)

            headers = self.credentials.auth_headers

            # Use the JSON API by default, but remember we might request a PDF (application/pdf)
            # so don't force the Accept header.
            if 'Accept' not in headers:
                headers['Accept'] = 'application/json'

            # Set a user-agent so Exo knows the traffic is coming from pyExo
            # or individual user/partner
            headers['User-Agent'] = self.user_agent

            response = getattr(requests, method)(
                    uri, data=body, headers=headers,
                    params=params, timeout=timeout)

            if response.status_code in [200, 201, 202]:
                # If we haven't got JSON, assume we're being returned a binary file
                if not response.headers['content-type'].startswith('application/json'):
                    return response.content

                return self._parse_api_response(response, self.name)

            elif response.status_code == 400:
                raise ExoBadRequest(response)

            elif response.status_code == 401:
                raise ExoUnauthorised(response)

            elif response.status_code == 403:
                raise ExoForbidden(response)

            elif response.status_code == 404:
                raise ExoNotFound(response)

            elif response.status_code == 500:
                raise ExoInternalError(response)

            else:
                raise ExoExceptionUnknown(response)

        return wrapper
