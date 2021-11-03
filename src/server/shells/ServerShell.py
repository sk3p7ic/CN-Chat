import cmd  # Used to create a command shell
import logging  # Used to log messages

from time import ctime

import server.db.DBManager as DBManager


DATABASE_NAME = None

logging.basicConfig(level=logging.INFO)

# TODO: Move this method somewhere else
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


class MasterChatServerShell(cmd.Cmd):
    intro = "Started the server shell. Type 'help' or '?' to list commands.\n"  # Displayed on startup
    prompt = "[ SHELL ]$>> "  # The prompt displayed for the shell
    database_manager = None

    def preloop(self):
        # Create the manager for the database
        global DATABASE_NAME
        self.database_manager = DBManager.DatabaseManager(DATABASE_NAME, "")

    def precmd(self, line):
        return line.lower()  # Convert the line to lowercase

    def do_quit(self, arg):
        """Quits the server."""
        log_server_msg(logging.INFO, "Stopping the server...")
        return True

    def do_exit(self, arg):
        """Quits the server."""
        return self.do_quit(arg)

    def do_stop(self, arg):
        """Quits the server."""
        return self.do_quit(arg)

    def do_listtables(self, args):
        """Lists the tables in the database.
        Usage: $ listtables [-v, --verbose]

        Optional Flags:
        -v, --verbose - Show the table info with the 'tableinfo' command as tables are listed.
        """
        if "-v" in args or "--verbose" in args:
            self.list_tables(True)  # List the tables verbosely
        else:
            self.list_tables(False)  # Give the standard list of tables

    def do_showtable(self, args):
        """Shows the layout of a specified table.
        Usage: $ showtable [-l, --list] <tablename>

        Optional Flags:
        -l, --list - List the tables in the database by calling the 'listtables' command. Using this flag will ignore
                     all other options.

        Valid tablename options:
        *          - Show all tables.
        tablename  - Show the table matching name 'tablename'.
        """
        if "-l" in args or "--list" in args:  # Check if the user would like to list the tables
            self.list_tables(True)  # List the tables verbosely
        arg_list = args.split(' ')  # Get a list from the args
        tablename = arg_list[-1]  # Get the tablename from the last element
        type(tablename)
        self.database_manager.show_table_info(tablename.strip())

    def do_dig(self, arg):
        """Shows the contents of a given tablename."""
        try:
            self.database_manager.show_table_contents(arg)
        except Exception as err:
            log_server_msg(logging.WARN, err.__str__())

    def list_tables(self, is_verbose):
        self.database_manager.show_all_tables(is_verbose)  # Display the tables in the database


def start_shell(database_name):
    global DATABASE_NAME
    DATABASE_NAME = database_name
    MasterChatServerShell().cmdloop()  # Start the shell
    return True  # Return true when the shell finishes
