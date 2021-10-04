import hashlib
import secrets

from server.db.DBManager import DatabaseManager


class TokenManager(DatabaseManager):

    def verify_token(self, user_id: int, token: str):
        """
        Verifies that a given token matches a given user_id.
        :param user_id: The user_id of the user to verify.
        :param token: The token of the user to verify.
        :return: True / False if the user is valid / invalid, respectively.
        """
        users = self.cursor.execute("SELECT user_id FROM app_users WHERE "
                                    "token = ?", token)
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

        token = secrets.token_hex(16)  # Generate a new token for the user
        # Insert the user into the database
        self.cursor.execute("INSERT INTO app_users (username, password, token) "
                            "VALUES (?, ?, ?)", (username,
                                                 hash_password(),
                                                 token))
        # Get the user_id of the newly-added user
        user_id = self.cursor.execute("SELECT user_id FROM app_users WHERE "
                                      "username = ? AND token = ?",
                                      (username, token))
        return user_id, token