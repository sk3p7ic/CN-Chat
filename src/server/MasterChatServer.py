import socket
import threading

from time import time

import server.db.DBManager as DBMgr
import server.auth.TokenManager as TokenMgr

from common.RequestStructures import MsgTypes

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port

database_manager = DBMgr.DatabaseManager("test")
TOKEN_MANAGER = TokenMgr.TokenManager(database_manager)
SERVER_QUIT = False


def accept_connections(server: socket):
    while not SERVER_QUIT:
        client, client_addr = server.accept()
        print(f"[SERVER] Connection from {client_addr} at {time()}")


def run_master_server(host=None, port=None):
    if host is None:
        host = HOST
    if port is None:
        port = PORT
