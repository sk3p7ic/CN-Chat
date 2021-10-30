import configparser
import socket

import client.MainWindow
import client.LoginWindow


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")  # Read the config file
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 42069))
        username, password = client.LoginWindow.start(config, sock)
        print(f"{username} -- {password}")


if __name__ == "__main__":
    main()
