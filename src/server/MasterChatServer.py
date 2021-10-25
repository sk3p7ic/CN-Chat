import socket
import logging
import threading

from time import ctime

import server.db.DBManager as DBMgr
import server.auth.TokenManager as TokenMgr
import common.RequestStructures as RequestStructures

from common.RequestStructures import BUFF_SIZE  # Import this var directly
from server.ServerPool import ServerPool

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port

DATABASE_MANAGER = DBMgr.DatabaseManager("test")
TOKEN_MANAGER = TokenMgr.TokenManager(DATABASE_MANAGER)
SERVER_QUIT = False

SERVER_POOL = ServerPool()

logging.basicConfig(level=logging.INFO)


def log_server_msg(level: [int, str], msg: str):
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


def accept_connections(server: socket):
    """
    Accepts new connections to the server.
    :param server: socket.socket object containing the main socket that the server is listening on.
    :return: None.
    """
    while not SERVER_QUIT:
        client, client_addr = server.accept()  # Accept the connection
        log_server_msg(logging.INFO, f"Connection from {client}:{client_addr}")
        data = client.recv(BUFF_SIZE)
        message = RequestStructures.get_message_from_json(data.decode("utf8"))
        user_auth_str = message.get_json()["message"]  # Get the message content
        if user_auth_str == "-1":
            pass
        else:
            # Get the user_id and token for the user from the message that was sent
            user_id = user_auth_str.split("\n")[0]
            user_token = user_auth_str.split("\n")[1]
            # Verify that the token is valid
            is_valid_token = TOKEN_MANAGER.verify_token(user_id, user_token)
            if is_valid_token:
                log_server_msg(logging.INFO, f"Successful login from {client} (user_id: {user_id})")
                user_info = ServerUser(user_id, client, client_addr)
                threading.Thread(target=handle_logged_user, args=(user_info,))  # Start a new thread for client
            else:
                log_server_msg(logging.WARN, f"Failed login from {client} (user_id: {user_id})")


def handle_logged_user(user_info):
    """
    Adds a new user into the pool of logged in users and handles chat connections.
    :param user_info: ServerClient object containing information about the user / client.
    :return: None.
    """
    # TODO: Add code allowing the user to connect to a given chat (public / private) and start new chats
    destination_server = client.recv(BUFF_SIZE)
    if destination_server.decode("utf8") in SERVER_POOL.servers:
        pass  # TODO: Send user to server


def server_shell():
    log_server_msg(logging.INFO, "Starting server shell.")
    global SERVER_QUIT
    while not SERVER_QUIT:
        user_input = input()
        if user_input.lower() == "quit" or user_input.lower() == "stop":
            SERVER_QUIT = True


def run_master_server(host=None, port=None):
    if host is None:
        host = HOST
    if port is None:
        port = PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        shell_thread = threading.Thread(target=server_shell)
        shell_thread.start()
        server.bind((host, port))
        server.listen()
        log_server_msg(logging.INFO, f"Started listening for connections on {host}:{port}")
        server_thread = threading.Thread(target=accept_connections, args=(server,), daemon=True)
        server_thread.start()
        shell_thread.join()
