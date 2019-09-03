class ExoException(Exception):
    def __init__(self, response, msg=None):
        self.response = response
        super(ExoException, self).__init__(msg)
        

class ExoBadRequest(ExoException):
    # HTTP 400: Bad Request
    def __init__(self, response):
        super(ExoBadRequest, self).__init__(response, response.text)


class ExoUnauthorised(ExoException):
    # HTTP 401: Unauthorised
    def __init__(self, response):
        super(ExoUnauthorised, self).__init__(response, response.text)


class ExoForbidden(ExoException):
    # HTTP 403: Forbidden
    def __init__(self, response):
        super(ExoForbidden, self).__init__(response, response.text)


class ExoNotFound(ExoException):
    # HTTP 404: Resource Not Found
    def __init__(self, response):
        super(ExoNotFound, self).__init__(response, response.text)


class ExoTimeout(ExoException):
    # HTTP 408: Timeout
    def __init__(self, response):
        super(ExoTimeout, self).__init__(response, response.text)


class ExoRemoved(ExoException):
    # HTTP 410: Resource Removed
    def __init__(self, response):
        super(ExoRemoved, self).__init__(response, response.text)


class ExoInternalError(ExoException):
    # HTTP 500: Internal Error
    def __init__(self, response):
        super(ExoInternalError, self).__init__(response, response.text)


class ExoExceptionUnknown(ExoException):
    # Any other exception
    def __init__(self, response):
        super(ExoExceptionUnknown, self).__init__(response, response.text)


class ExoIncompleteAuthorisation(ExoException):
    # Incomplete authorisation data
    def __init__(self, response):
        super(ExoIncompleteAuthorisation, self).__init__(response, "Complete Exo authorisation in the"
                                                                   " '.env' configuration file")


