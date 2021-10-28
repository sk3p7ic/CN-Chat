import logging

from time import ctime


def log_server_msg(msg, log_level=logging.INFO):
    logging.basicConfig(level=log_level)
    log_msg = f"[{ctime()}]::SERVER $>>" + msg
    logging.info(log_msg)


class BaseSk3p7icException(Exception):
    """Base class for all exceptions I write."""
    pass