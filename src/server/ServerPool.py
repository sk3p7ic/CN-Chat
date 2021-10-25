from dataclasses import dataclass
import socket

from server.auth.Exceptions import InvalidMemberError


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
        # Check if server is set to private mode and if both clients have been given if the server is private
        if not is_public and (c_len := len(clients)) != 2:
            raise ValueError(f"Server is set to private and does not have 2 clients. (Supplied {c_len}).")
        if clients is not None and type(clients) is not dict:
            raise TypeError(f"Type of 'clients' is not dict. (Currently {type(clients)}).")
        new_server_id = sorted(servers)[-1] + 1  # Get last highest ID and add one
        # Add the server information to the database
        self.cursor.execute("INSERT INTO servers (server_id, server_name) VALUES (?, ?)",
                            (new_server_id, server_name))
        server_info = {
            "server_class": ChatServer(server_id, clients),
            "server_name": server_name,
            "is_public": is_public,
            "clients": clients
        }
        self.servers[new_server_id] = server_info


    def add_client(self, client_id, client_socket, client_address, current_server=None):
        self.clients[client_id] = UserConnectionInfo(client_socket, client_address, current_server)


    def transfer_client(self, client_id, server_id):
        server_info = None
        try:
            server_info = self.servers[server_id]
            if client_id not in server_info.get("clients"):  # If the client is not listed as a member of server
                raise InvalidMemberError(client_id, server_id)
        except KeyError:
            raise KeyError(f"Server ID, '{server_id}', is not a valid server ID.")
        if client_id not in self.clients:
            raise KeyError(f"Client with client ID '{client_id}' has not been registered to the server pool.")
        # Add the client to the server
        self.servers[server_id]["server_class"].add_client(client_id, self.clients[client_id])
        # TODO: Check if server is running and transfer client socket to that server
        # TODO: If server not running, start the server


    def list_public_servers(self):
        server_list = []  # Stores the list of public servers
        for server_id in self.servers:
            server_info = self.servers[server_id]  # Get the information being stored about a server
            if server_info.get("is_public"):  # Get if the server is set to public
                # If server is public, append new tuple containing server id and server name
                server_list.append((server_id, server_info[1]))
        return server_list


def ChatServer:
    clients = {}

    def __init__(self, server_id, clients=None):
        self.server_id = server_id
        if clients is not None:
            if type(clients) is dict: self.clients = clients
            else: raise TypeError(f"Invalid type, {type(clients)} for clients.")


    def add_client(self, client_id, client_info):
        self.clients[client_id] = client_info

