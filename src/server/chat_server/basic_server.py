
SERVER_TYPES = [
    "PRIVATE_CHAT",
    "PUBLIC_SERVER"
]

class BasicServer:
    def __init__(self, server_port, server_type):
        """
        Creates a new instance of a basic server.

        Parameters:
        -----------
        server_port : int
            The port number that will be used to run the server.
        server_type : int
            The type of the server, as defined in SERVER_TYPES.
        
        Raises:
        -------
        ValueError:
            If the server_type that is supplied is not a valid server type as
            defined in SERVER_TYPES.
        """
        self.port = server_port
        if server_type not in SERVER_TYPES:
            raise ValueError(f"Value {server_type} is not a valid type.")
        self.type = server_type