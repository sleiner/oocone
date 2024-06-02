class OoconeError(Exception):
    """Base class for oocone."""


class AuthenticationFailed(OoconeError):
    """Authentication has failed."""


class UnexpectedResponse(OoconeError):
    """Got unexpected data back from the enocoo website"""
