import socket


def get_hostname():
    return "127.0.0.1"


def get_port():
    return 42069


class MainPrivateChatServer:
    def __int__(self, hostname=None, port=None):
        self.hostname = hostname if hostname is not None else get_hostname()
        self.port = port if port is not None else get_port()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.hostname, self.port))  # Bind the socket to the port
            s.listen()  # Start listening for connections
            print(f"[*] Listening on {self.hostname}:{self.port}...")
            s.setblocking(False)  # Set blocking to False
