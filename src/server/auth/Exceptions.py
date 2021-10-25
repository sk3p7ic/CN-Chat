import logging

from time import ctime


class InvalidMemberError(Exception):
    # TODO: Refine this class to take better inputs and output a standardized message
    def __init__(self, user_id, server_id, msg=None):
        """
        Exception raised when the user attempts to connect to a server which is private and they are not a member of.

        Parameters:
        :param user_id: int containing the user_id of the user attempting to connect to the server.
        :param server_id: int containing the server_id of the server the user is attempting to connect to.
        :param msg: str containing a custom message, if wanted.
        """
        if msg is None:
            msg = f"Failed attempt from user {user_id} connecting to server {server_id}. "
            msg += "User is not a member of this server."
        self.msg = msg
        logging.basicConfig(level=logging.INFO)
        log_msg = f"[{ctime()}]::SERVER $>>" + self.msg
        logging.info(msg)
        # TODO: Log entry into database for failed attempts


    def __str__(self):
        return repr(self.msg)
