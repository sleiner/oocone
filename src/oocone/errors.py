class OoconeError(Exception):
    """Base class for oocone."""


class ConnectionError(OoconeError):
    """Could not connect to the enocoo website."""


class AuthenticationFailed(OoconeError):
    """Authentication has failed."""


class UnexpectedResponse(OoconeError):
    """Got unexpected data back from the enocoo website"""
