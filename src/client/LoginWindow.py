import tkinter as tk
import configparser
import hashlib  # Used to hash the password(s) the user enters
import os.path  # Used to check if the tokenfile exists

from common.RequestStructures import *


class LoginWindow(tk.Frame):
    def __init__(self, tk_root, config, server):
        """
        Creates the Login Window for the application.

        Parameters:
        :param tk_root: The root window for the tkinter application.
        :param config: The config settings for the application.
        :param server: socket.socket socket connection to the main CN-Chat server.
        """
        # Set main class variables
        self.root = tk_root
        self.config = config
        self.server = server
        # Further initialize tkinter
        super().__init__(tk_root)
        self.pack()
        # Create the labels
        self.username_label = tk.Label(text="Username")
        self.password_label = tk.Label(text="Password")
        # Create the variables that will store user input
        self.tk_username = tk.StringVar()
        self.tk_password = tk.StringVar()
        # Create the entry boxes for the user
        self.username_box = tk.Entry(width=25, textvariable=self.tk_username)
        self.password_box = tk.Entry(width=25, textvariable=self.tk_password, show='*')
        # Pack everthing
        self.username_label.pack()
        self.username_box.pack()
        self.password_label.pack()
        self.password_box.pack()
        # Create the submit button
        self.submit_btn = tk.Button(text="Submit", command=self.submit)
        self.submit_btn.pack()
        # Display everything
        tk_root.mainloop()

    def submit(self):
        """Called when the user clicks the submit button."""
        # Get the values from the Entry widgets
        self.username = self.tk_username.get()
        self.password = self.tk_password.get()
        # Attempt to authenticate the user
        is_authenticated = self.attempt_validation()
        # TODO: Destroy this window if True
        self.root.destroy()

    def attempt_validation(self):
        """Attempts to authenticate the user with their username and password. Returns True if successful."""
        # TODO: Handle if authentication fails and allow the user to try again
        # TODO: Handle if the user would like to make a new account
        token, user_id, response_code = self.get_token()
        if response_code == 0:
            message = Message(user_id, bytes(token, "utf8"), MsgTypes.MSG_NAME)
            # Send the json string to the server
            self.server.send(bytes(message.get_json_str(), "utf8"))
            data = self.server.recv(BUFF_SIZE)
            server_msg = get_message_from_json(data.decode("utf8"))  # Decode and get the Message that was recieved
            if get_type_from_str(server_msg.get_json()["msg_type"]) is MsgTypes.MSG_PASS:
                print("We were logged in")
                return True
            elif get_type_from_str(server_msg.get_json()["msg_type"]) is MsgTypes.MSG_FAIL:
                pass
        elif response_code == 1:  # If the tokenfile did not exist, create the new user
            message = Message(-1, b"-1", MsgTypes.MSG_NAME)
            # Send the json string to the server
            self.server.send(bytes(message.get_json_str(), "utf8"))
            data = self.server.recv(BUFF_SIZE)
            server_msg = get_message_from_json(data.decode("utf8"))  # Decode and get the Message that was recieved
            if get_type_from_str(server_msg.get_json()["msg_type"]) is not MsgTypes.MSG_FAIL:
                print("There was an error.")
                return False
            else:
                # Create the message with the new user info to send to the server
                message = Message(-1, bytes(f"{self.username} {hashlib.md5(self.password.encode()).hexdigest()}",
                                            "utf8"), MsgTypes.MSG_NAME)
                # Send the json string to the server
                self.server.send(bytes(message.get_json_str(), "utf8"))
                data = self.server.recv(BUFF_SIZE)
                server_msg = get_message_from_json(data.decode("utf8"))  # Decode and get the Message that was recieved
                if get_type_from_str(server_msg.get_json()["msg_type"]) is MsgTypes.MSG_NAME:
                    content = server_msg.get_json()["message"]
                    user_id, token = content.split('\n')  # Split the content sent by server and unpack
                    self.write_token(user_id, token)  # Write the information to the tokenfile
                else:  # If there was some kind of error
                    print(server_msg.get_json()["message"])
                    return False
        return False

    def get_inputs(self):
        """Returns the inputs that the user gave for ther username and password"""
        return self.username, self.password

    def write_token(self, user_id, token):
        """Writes the token and user information to the tokenfile."""
        tokenfile_path = self.config["DEFAULT"]["tokenfile_location"]  # Get the location of the tokenfile
        with open(tokenfile_path, 'w') as tokenfile:
            lines = f"{self.username} {hashlib.md5(self.password.encode()).hexdigest()} {user_id}\n{token}\n"
            tokenfile.write(lines)  # Write the lines to the file

    def get_token(self):
        """
        Gets the token from the tokenfile.

        :return: If the username and password are correct and the tokenfile exists, the token, user_id, and a response
                 code of 0 to show successful operation. Otherwise None is returned for the token and -1 for the
                 user_id. The other response codes are as follows:
                 1: The tokenfile does not exist.
                 2: The tokenfile is empty.
                 3: The tokenfile contains too many lines or is not properly formatted.
        """
        tokenfile_path = self.config["DEFAULT"]["tokenfile_location"]  # Get the location of the tokenfile
        if os.path.exists(tokenfile_path):  # If the tokenfile exists, continue
            with open(tokenfile_path, 'r') as tokenfile:  # Open the tokenfile
                contents = tokenfile.read()  # Get the contents of the file
                if len(contents) == 0:  # If there's nothing in the file
                    print("ERROR: There is nothing in the token file!")
                    return None, -1, 2
                lines = contents.split('\n')  # Get the lines of the file
                if lines[-1] == '': del lines[-1]  # Remove the last line if it's empty
                if (line_length := len(lines)) != 2:
                    print(f"ERROR: Length of lines is not 2 (currently {line_length})!")
                    return None, -1, 3
                username, password, user_id = lines[0].split(' ')
                if username == self.username and password == hashlib.md5(self.password.encode()).hexdigest():
                    return lines[1], user_id, 0  # This line will contain the token
        else:  # If the tokenfile does not exist
            print("ERROR: Tokenfile does not exist!")
            return None, -1, 1


def start(config, server, root=None):
    # Create the root window if it's not given
    if root is None:
        root = tk.Tk()
    root.title("CN-Chat Client :: Login")  # Set the title
    login_window = LoginWindow(root, config, server)  # Start the app and wait for user input
    username, password = login_window.get_inputs()  # Get what the user input
    # TODO: Validate before killing login window
    return username, password  # Return the username and password that the user gave
