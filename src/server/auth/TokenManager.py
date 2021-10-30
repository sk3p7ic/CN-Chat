import hashlib
import secrets

from server.db.DBManager import DatabaseManager


class TokenManager:

    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager
        self.cursor = self.database_manager.get_cursor()
        self.connection = self.database_manager.get_connection()

    def verify_token(self, user_id: int, token: str):
        """
        Verifies that a given token matches a given user_id.
        :param user_id: The user_id of the user to verify.
        :param token: The token of the user to verify.
        :return: True / False if the user is valid / invalid, respectively.
        """
        users = self.cursor.execute("SELECT user_id FROM app_users WHERE "
                                    "token = ?", token).fetchall()
        if len(users) != 1 or str(users[0]) != str(user_id):
            return False
        else:
            return True

    def add_user(self, username: str, password: str):
        """
        Adds a new user to the database and returns their user ID and token.
        :param username: The username for the user that will be added.
        :param password: The password for the user that will be added.
        :return: The user ID and token for the newly-added user.
        """

        def hash_password():
            return hashlib.md5(password.encode()).hexdigest()

        # Check if the username already exists
        test_user_id = self.cursor.execute(f"SELECT user_id FROM app_users WHERE username='{username}';").fetchall()
        if len(test_user_id) != 0:
            return (False, "Username already exists."), -1, secrets.token_hex(16)
        token = secrets.token_hex(16)  # Generate a new token for the user
        # Insert the user into the database
        self.cursor.execute("INSERT INTO app_users (user_id, username, password, token) "
                            "VALUES (?, ?, ?, ?)", (self.database_manager.get_app_user_table_size() + 2,
                                                    username,
                                                    hash_password(),
                                                    token))
        # Get the user_id of the newly-added user
        user_id = self.cursor.execute("SELECT user_id FROM app_users WHERE "
                                      "username = ? AND token = ?",
                                      (username, token)).fetchall()
        self.connection.commit()  # Commit the changes
        return (True, ""), user_id[0][0], token

    def add_test_user(self):
        print(self.add_user("test_user", "Bruichladdich"))
