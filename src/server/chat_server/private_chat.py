import chat_server.basic_server

class PrivateChat(chat_server.basic_server.BasicServer):
    def __init__(self, owner_user_id, other_user_id):
        """
        Creates a new server for a private chat between two users.

        Parameters:
        -----------
        owner_user_id : int
            The UID of the "owner" of the chat. That is, the UID of the user who
            started the chat.
        other_user_id : int
            The UID of the user who is being messaged by the owner.
        """
        self.owner_id = owner_user_id
        self.other_id = other_user_id