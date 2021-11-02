import sqlite3
from contextlib import closing
from os import getcwd
from time import ctime
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
            for table in tables:
                table_data = cursor.execute(f"PRAGMA table_info({table[0]});").fetchall()
                output = f"[{ctime()}]::SERVER $>> LOADED TABLE: `{table[0]}`:\n"
                output += f"{'col_name':25}    {'col_type':15}    {'not_null':15}    {'default_value':15}\n"
                output += f"{'-'*25}    {'-'*15}    {'-'*15}    {'-'*15}\n"
                for col_id, name, data_type, not_null, def_value, is_pk in table_data:
                    not_null = bool(not_null)  # Explicitly convert this value
                    name = ("* " + name) if is_pk else ("  " + name)
                    if def_value is None: def_value = ""
                    output += f"{name:25}    {data_type:15}    {not_null!s:<15}    {def_value:15}\n"
                table_size = len(cursor.execute(f"SELECT * FROM {table[0]};").fetchall())
                if table_size == -1:  # If the table is empty
                    table_size = 0
                output += f"Table Size: {table_size} entries.\n"
                logging.info(output)
            connection.commit()  # Commit the changes


class DatabaseManager:
    def __init__(self, db_name: str, ddl_path, startup=False):
        if ".db" not in db_name:  # Check if db_name is a filename
            db_name += ".db"
        # TODO: Better handling of the ddl path
        ddl_path = getcwd() + ddl_path
        if startup:
            create_db(db_name, ddl_path)
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # Connect to db
        self.cursor = self.connection.cursor()  # Create cursor to run queries

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.connection

    def get_app_user_table_size(self):
        return len(self.cursor.execute(f"SELECT * FROM app_users;").fetchall())
