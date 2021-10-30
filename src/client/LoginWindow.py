import tkinter as tk
from time import sleep

class LoginWindow(tk.Frame):
    def __init__(self, tk_root):
        self.root = tk_root
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
        self.root.destroy()

    def get_inputs(self):
        """Returns the inputs that the user gave for ther username and password"""
        return self.username, self.password


def start(root=None):
    # Create the root window if it's not given
    if root is None:
        root = tk.Tk()
    root.title("CN-Chat Client :: Login")  # Set the title
    login_window = LoginWindow(root)  # Start the app and wait for user input
    username, password = login_window.get_inputs()  # Get what the user input
    # TODO: Validate before killing login window
    return username, password  # Return the username and password that the user gave
