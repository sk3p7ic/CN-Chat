import socket
import logging
import threading

from time import ctime

import server.db.DBManager as DBMgr
import server.auth.TokenManager as TokenMgr
import common.RequestStructures as RequestStructures

from server.auth.Exceptions import InvalidMemberError, ServerNotStartedError
from common.RequestStructures import BUFF_SIZE  # Import this var directly
from server.ServerPool import ServerPool

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port

DBMgr.DatabaseManager("test", "/server/db/sql/create_db.ddl", True)  # Initialize database
SERVER_QUIT = False

server_pool = ServerPool(DBMgr.DatabaseManager("test", "/server/db/sql/create_db.ddl"))

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


def create_new_user(client, token_manager: TokenMgr.TokenManager):
    """
    Creates a new user in the database.
    :param client: The socket being used to communicate with the client.
    :param token_manager: The TokenManager that will be used to create the new user, their token, and verify that they
                          have been added to the database.
    :return: True if the user was successfully added; False if there was an error. Also returns the user_id of the newly
             created user.
    """
    # Send the client a message to let them know that authentication failed
    message = RequestStructures.Message(0, b'', RequestStructures.MsgTypes.MSG_FAIL)
    client.send(bytes(message.get_json_str(), "utf8"))
    # Get the response from the user containing their desired username and password
    data = client.recv(BUFF_SIZE)
    # Decode and get the Message that was received
    usr_msg = RequestStructures.get_message_from_json(data.decode("utf8"))
    # Convert the Message into a dict, get the "msg_type", convert to a MsgType, and verify that it is a MSG_NAME
    if RequestStructures.get_type_from_str(usr_msg.get_json()["msg_type"]) is RequestStructures.MsgTypes.MSG_NAME:
        # Get the username and password the user wants to use from the content that they sent
        usr_auth_str = usr_msg.get_json()["message"]
        username, password = usr_auth_str.split(' ')  # Get the username and password that was sent and unpack
        status, user_id, user_token = token_manager.add_user(username, password)  # Attempt to add user to database
        if not status[0]:
            message = RequestStructures.Message(0, bytes("Error: " + status[1], "utf8"),
                                                RequestStructures.MsgTypes.MSG_FAIL)
            client.send(bytes(message.get_json_str(), "utf8"))
            data = client.recv(BUFF_SIZE)
            return False, -1
        # Double check that the user is now valid in the database
        if token_manager.verify_token(user_id, user_token):
            message = RequestStructures.Message(0, bytes(f"{user_id}\n{user_token}", "utf8"),
                                                RequestStructures.MsgTypes.MSG_NAME)
            client.send(bytes(message.get_json_str(), "utf8"))
            data = client.recv(BUFF_SIZE)
            usr_msg = RequestStructures.get_message_from_json(data.decode("utf8"))
            if get_type_from_str(usr_msg.get_json()["msg_type"]) is RequestStructures.MsgTypes.MSG_PASS:
                return True, user_id
    else:
        return False, -1


def accept_connections(server: socket):
    """
    Accepts new connections to the server.
    :param server: socket.socket object containing the main socket that the server is listening on.
    :return: None.
    """
    global server_pool
    database_manager = DBMgr.DatabaseManager("test", "/server/db/sql/create_db.ddl")
    token_manager = TokenMgr.TokenManager(database_manager)
    while not SERVER_QUIT:
        client, client_addr = server.accept()  # Accept the connection
        log_server_msg(logging.INFO, f"Connection from {client}:{client_addr}")
        try:
            data = client.recv(BUFF_SIZE)
            message = RequestStructures.get_message_from_json(data.decode("utf8"))
            user_token = message.get_json()["message"]  # Get the message content
            if user_token == "-1":
                user_added, user_id = create_new_user(client, token_manager)
                if user_added:  # If the user was sucessfully added
                    user_info = (user_id, client, client_addr)
                    client_thread = threading.Thread(target=handle_logged_user, args=(user_info,))
                    client_thread.start()
                    client_thread.join()
            else:
                # Get the user_id and token for the user from the message that was sent
                user_id = message.get_json()["user_id"]
                # Verify that the token is valid
                is_valid_token = token_manager.verify_token(user_id, user_token)
                if is_valid_token:
                    log_server_msg(logging.INFO, f"Successful login from {client} (user_id: {user_id})")
                    user_info = (user_id, client, client_addr)
                    client_thread = threading.Thread(target=handle_logged_user, args=(user_info,))
                    client_thread.start()
                    client_thread.join()
                else:
                    log_server_msg(logging.WARN, f"Failed login from {client} (user_id: {user_id})")
                    # TODO: Log this message in another security file as well
        except Exception as err:
            log_server_msg(logging.ERROR, f"Error in connection {client_addr}: {err}")
        finally:
            # If this statement is readched, it means that there was a disconnect, so print that to the terminal
            log_server_msg(logging.INFO, f"Disconnect from connection {client_addr}")


def handle_logged_user(user_info):
    """
    Adds a new user into the pool of logged in users and handles chat connections.
    :param user_info: ServerClient object containing information about the user / client.
    :return: None.
    """
    # TODO: Add code allowing the user to connect to a given chat (public / private) and start new chats
    # Let the user know that they were sucessfully logged in
    print("I at least got here! *cries*")
    user_id, client, client_addr = user_info
    message = RequestStructures.Message(0, b'', RequestStructures.MsgTypes.MSG_PASS)
    client.send(bytes(message.get_json_str(), "utf8"))
    print("Sent {}".format(message))
    server_pool.add_client(user_id, client, client_addr)  # Add the client to pool of clients in server pool
    destination_server = client.recv(BUFF_SIZE)
    if (server_id := destination_server.decode("utf8")) in server_pool.servers:
        try:
            server_pool.transfer_client(user_id, server_id)
        except ServerNotStartedError as err:  # Shouldn't happen because the server is in server_pool.servers
            log_server_msg(logging.ERROR, err.msg)  # Log the error
            pass
        except InvalidMemberError as err:  # If the client somehow doesn't exist in the server_pool
            log_server_msg(logging.ERROR, err.msg)  # Log the error
            # TODO: End client session and log to separate file about the incident
        except Exception as err:  # Catch any other errors
            pass  # TODO: Handle the exception


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
