#!/usr/bin/env python3

import logging  # Used to log messages
from time import ctime  # Used to get the time


logging.basicConfig(level=logging.INFO)


def log_server_msg(level: int, msg: str):
    """
    Logs a given message at a given level with a set format.
    :param level: The logging level of the message.
    :param msg: The message you want to log.
    :return: None.
    """
    msg = f"[{ctime()}]::SERVER $>> " + msg
    if level is logging.INFO:
        logging.info(msg)
    elif level is logging.WARNING:
        logging.warning(msg)
    elif level is logging.ERROR:
        logging.error(msg)
    elif level is logging.CRITICAL:
        logging.critical(msg)
