import tkinter as tk


class MainWindow:
    def __init__(self, tk_root):
        self.root = tk_root

def start(root=None):
    """
    Used to start the GUI application.

    Parameters:
    :param root: The root window for the tk application
    """
    if root is None:
        root = tk.Tk()  # Create the root window
    root.title("CN-Chat Client")  # Set the title of the window
    main_window = MainWindow(root)  # Start the main window class
