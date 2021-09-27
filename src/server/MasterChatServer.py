import socket
import threading
import socketserver

from common.RequestStructures import MsgTypes, Message

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port


class MasterChatServerHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        data = self.request.recv(50).strip()
        header = Message(0, MsgTypes.MSG_NORM, )


def run_master_server(host=None, port=None):
    if host is None:
        host = HOST
    if port is None:
        port = PORT

    # Create the server, binding to host on port
    with socketserver.TCPServer((host, port), MasterChatServerHandler) as s:
        s.serve_forever()
