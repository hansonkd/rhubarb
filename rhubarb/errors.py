class RhubarbException(Exception):
    pass


class RhubarbValidationError(RhubarbException):
    pass


class PermissionDenied(RhubarbException):
    pass
