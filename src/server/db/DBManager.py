import sqlite3
from contextlib import closing
from os import path
import logging
import secrets

logging.basicConfig(level=logging.INFO)


def create_db(db_name):
    if ".db" not in db_name:  # Check if db_name is a filename
        db_name += ".db"
    if path.isfile(db_name):  # Check if database file already exists
        logging.warning("Database has already been created.")
        return
    with closing(sqlite3.connect(db_name)) as connection:
        with closing(connection.cursor()) as cursor:
            # Create the table for the users
            create_cmd = "CREATE TABLE app_users(user_id INTEGER PRIMARY KEY "
            create_cmd += "ASC, username TEXT, password TEXT, token TEXT)"
            cursor.execute(create_cmd)
            logging.info("Created table `app_users` for users.")
            # Add record for the server
            add_cmd = "INSERT INTO app_users (username, password, token) "
            add_cmd += "VALUES (\"server\", \"Bruichladdich\", \"{}\")".format(
                secrets.token_hex(16)
            )
            cursor.execute(add_cmd)
            logging.info("Inserted 'server' user into the `app_users` table.")


class DatabaseManager:
    def __init__(self, db_name: str):
        if ".db" not in db_name:  # Check if db_name is a filename
            db_name += ".db"
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # Connect to db
        self.cursor = self.connection.cursor()  # Create cursor to run queries
