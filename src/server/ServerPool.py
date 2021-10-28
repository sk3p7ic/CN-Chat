from dataclasses import dataclass
import socket

from server.auth.Exceptions import InvalidMemberError, ServerNotStartedError


@dataclass
class UserConnectionInfo:
    client_socket: socket.socket
    client_address: str
    current_server: int


class ServerPool:
    servers = {}
    clients = {}

    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.cursor = self.database_manager.get_cursor()


    def add_server(self, server_name, is_public, clients=None):
        """
        Adds a server to the pool of available servers.

        Parameters:
        :param server_name: str containing the name of the server.
        :param is_public: bool representing whether the server is public or not.
        :clients: dict of UserConnectionInfo objects containing information about users. Used mainly for private
                  servers.

        Throws: TypeError, ValueError
        """
        # Check inputs to make sure that they are using the correct types
        if type(is_public) is not bool:
            raise TypeError(f"Type of 'is_public' is not dict. (Currently {type(is_public)}).")
        if clients is not None and type(clients) is not dict:
            raise TypeError(f"Type of 'clients' is not dict. (Currently {type(clients)}).")
        # Check if server is set to private mode and if both clients have been given if the server is private
        if not is_public and (c_len := len(clients)) != 2:
            raise ValueError(f"Server is set to private and does not have 2 clients. (Supplied {c_len}).")
        new_server_id = sorted(self.servers)[-1] + 1  # Get last highest ID and add one
        # Add the server information to the database
        self.cursor.execute("INSERT INTO servers (server_id, server_name) VALUES (?, ?)",
                            (new_server_id, server_name))
        server_info = {
            "server_class": ChatServer(new_server_id, clients),
            "server_name": server_name,
            "is_public": is_public,
            "clients": clients
        }
        self.servers[new_server_id] = server_info


    def add_client(self, client_id, client_socket, client_address, current_server=None):
        """
        Adds a client to the dict of clients in the server pool.

        Parameters:
        :param client_id: int containing the client_id of the client being added.
        :param client_socket: socket.socket object containing the socket that the user is connected with.
        :param client_address: str contianing the IP address of the client.
        :param current_server: int containing the server_id of the server the the user is currently connected to. If
                               set, attemps to connect the user to that sever via transfer_client().
        """
        self.clients[client_id] = UserConnectionInfo(client_socket, client_address, current_server)
        if current_server is not None:
            try:
                self.transfer_client(client_id, current_server)
            except ServerNotStartedError:
                # Start the server and attempt to connect the user to it
                pass  # TODO: Write code that does process descibed above


    def transfer_client(self, client_id, server_id):
        """
        Transfers a client to the given server.

        Parameters:
        :param client_id: int containing the client_id of the client attempting to connect to the server.
        :param server_id: int containing the server_id that the client is trying to connect to.

        Throws: InvalidMemberError, ServerNotStartedError, KeyError
        """
        server_info = None
        try:
            server_info = self.servers[server_id]
            # If the client is not listed as a member of a private server
            if not bool(server_info.get("is_public")) and client_id not in server_info.get("clients"):
                raise InvalidMemberError(client_id, server_id)
        except KeyError:
            raise ServerNotStartedError(server_id)
        if client_id not in self.clients:
            raise KeyError(f"Client with client ID '{client_id}' has not been registered to the server pool.")
        # Because the code in the try block would throw a KeyError if the server was not running, it can be assumed
        # that it is, therefore we just add the client to the server
        self.servers[server_id]["server_class"].add_client(client_id, self.clients[client_id])
        # TODO: If server not running, start the server


    def list_public_servers(self):
        """Returns a list of tuples of the server_id and server_name fields for the public servers in the pool."""
        server_list = []  # Stores the list of public servers
        for server_id in self.servers:
            server_info = self.servers[server_id]  # Get the information being stored about a server
            if server_info.get("is_public"):  # Get if the server is set to public
                # If server is public, append new tuple containing server id and server name
                server_list.append((server_id, server_info[1]))
        return server_list


class ChatServer:
    clients = {}

    def __init__(self, server_id, clients=None):
        self.server_id = server_id
        if clients is not None:
            if type(clients) is dict: self.clients = clients
            else: raise TypeError(f"Invalid type, {type(clients)} for clients.")


    def add_client(self, client_id, client_info):
        self.clients[client_id] = client_info

