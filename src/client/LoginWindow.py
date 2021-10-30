import configparser
import os.path
import hashlib
import tkinter as tk
from time import sleep

from common.RequestStructures import *


class LoginWindow(tk.Frame):
    def __init__(self, tk_root, config, server):
        self.root = tk_root
        self.config = config
        self.server = server
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
        self.username = self.tk_username.get()
        self.password = self.tk_password.get()
        is_authenticated = self.attempt_validation()
        # TODO: Destroy this window if True
        self.root.destroy()

    def attempt_validation(self):
        token, user_id, response_code = self.get_token()
        if response_code == 0:
            message = Message(user_id, bytes(token, "utf8"), MsgTypes.MSG_NAME)
            # Send the json string to the server
            self.server.send(bytes(message.get_json_str(), "utf8"))
            print("sent")
            data = self.server.recv(BUFF_SIZE)
            server_msg = get_message_from_json(data.decode("utf8"))  # Decode and get the Message that was recieved
            if get_type_from_str(server_msg.get_json()["msg_type"]) is MsgTypes.MSG_PASS:
                print("We were logged in")
                return True
        return False

    def get_inputs(self):
        """Returns the inputs that the user gave for ther username and password"""
        return self.username, self.password

    def get_token(self):
        tokenfile_path = self.config["DEFAULT"]["tokenfile_location"]
        print(tokenfile_path)
        if os.path.exists(tokenfile_path):
            with open(tokenfile_path, 'r') as tokenfile:
                contents = tokenfile.read()
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
        else:
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
