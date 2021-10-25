

class InvalidMemberError(Exception):
    """Exception raised when a client attempts to join a server that they do not have access to.

    Attributes:
        msg -- explaination of the error.
    """
    # TODO: Refine this class to take better inputs and output a standardized message
    # TODO: Maybe also log an entry in the logfile about the user's attempt?
    def __init__(self, msg):
        self.msg = msg


    def __str__(self):
        return repr(self.msg)
