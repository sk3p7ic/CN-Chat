import server.auth.TokenManager as TokenMgr
from common.RequestStructures import *


def create_new_user(client, token_manager: TokenMgr.TokenManager):
    """
    Creates a new user in the database.
    :param client: The socket being used to communicate with the client.
    :param token_manager: The TokenManager that will be used to create the new user, their token, and verify that they
    have been added to the database.
    :return: True if the user was successfully added; False if there was an error.
    """
    # Send the client a message to let them know that authentication failed
    message = Message(0, b'', MsgTypes.MSG_FAIL)
    client.send(bytes(message.get_json_str(), "utf8"))
    # Get the response from the user containing their desired username and password
    # TODO: Handle if the username is already taken by another user
    data = client.recv(BUFF_SIZE)
    usr_msg = get_message_from_json(data.decode("utf8"))  # Decode and get the Message that was received
    # Convert the Message into a dict, get the "msg_type", convert to a MsgType, and verify that it is a MSG_NAME
    if get_type_from_str(usr_msg.get_json()["msg_type"]) is MsgTypes.MSG_NAME:
        # Get the username and password the user wants to use from the content that they sent
        usr_auth_str = usr_msg.get_json()["message"]
        username = usr_auth_str.split("\n")[0]
        password = usr_auth_str.split("\n")[1]
        user_id, user_token = token_manager.add_user(username, password)  # Attempt to add user to database
        # Double check that the user is now valid in the database
        if token_manager.verify_token(user_id, user_token):
            message = Message(0, bytes(f"{user_id}\n{user_token}", "utf8"), MsgTypes.MSG_NAME)
            client.send(bytes(message.get_json_str(), "utf8"))
            data = client.recv(BUFF_SIZE)
            usr_msg = get_message_from_json(data.decode("utf8"))
            if get_type_from_str(usr_msg.get_json()["msg_type"]) is MsgTypes.MSG_PASS:
                return True
    else:
        return False
