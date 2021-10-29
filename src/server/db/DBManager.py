import sqlite3
from contextlib import closing
from os import getcwd
import logging
import secrets

logging.basicConfig(level=logging.INFO)


def create_db(db_name, ddl_path):
    if ".db" not in db_name:  # Check if db_name is a filename
        db_name += ".db"
    with closing(sqlite3.connect(db_name)) as connection:
        with closing(connection.cursor()) as cursor:
            # Import the sql used to create the server
            try:
                with open(ddl_path, 'r') as ddl_file:
                    # Execute the script to set up the database
                    cursor.executescript(ddl_file.read())
            except Exception as err:
                logging.error(f"Error creating database: {err}")
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';").fetchall()
            # TODO: Fix the formatting of the table display
            for table in tables:
                table_data = cursor.execute(f"PRAGMA table_info({table[0]});").fetchall()
                output = f"TABLE: `{table[0]}`:\n"
                output += "col_name\t\tcol_type\n"
                for entry in table_data:
                    output += f"{entry[1]}\t\t{entry[2]}\n"
                logging.info(output)
            connection.commit()  # Commit the changes


class DatabaseManager:
    def __init__(self, db_name: str, ddl_path):
        if ".db" not in db_name:  # Check if db_name is a filename
            db_name += ".db"
        # TODO: Better handling of the ddl path
        ddl_path = getcwd() + ddl_path
        create_db(db_name, ddl_path)
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # Connect to db
        self.cursor = self.connection.cursor()  # Create cursor to run queries

    def get_cursor(self):
        return self.cursor
