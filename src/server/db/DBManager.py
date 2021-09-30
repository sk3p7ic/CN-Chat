import sqlite3
from contextlib import closing
from os import path

from server.auth.TokenManager import Token


def create_db(db_name):
    if ".db" not in db_name:  # Check if db_name is a filename
        db_name += ".db"
    if path.isfile(db_name):  # Check if database file already exists
        return
    with closing(sqlite3.connect(db_name)) as connection:
        with closing(connection.cursor()) as cursor:
            # Create the table for the users
            cursor.execute("CREATE TABLE app_users(user_id INTEGER PRIMARY KEY"
                           "ASC, username TEXT, password TEXT, token TEXT")
            # Add record for the server
            cursor.execute("INSERT INTO app_users (user_id, username, password,"
                           " token) VALUES (NULL, \"server\", Bruichladdich, "
                           "?", (Token().get_token()))


class DatabaseManager:
    def __init__(self, db_name):
        if ".db" not in db_name:  # Check if db_name is a filename
            db_name += ".db"
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # Connect to db
        self.cursor = self.connection.cursor()  # Create cursor to run queries
