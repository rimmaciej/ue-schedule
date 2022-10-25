"""
Module with error definitions for the UE Katowice parser
"""


class WUTimeoutError(Exception):
    """
    Error for when request to Wirtualna Uczelnia timeouts
    """


class InvalidIdError(Exception):
    """
    Error for when the schedule id is considered invalid
    """


class WrongResponseError(Exception):
    """
    General wrong response error
    """