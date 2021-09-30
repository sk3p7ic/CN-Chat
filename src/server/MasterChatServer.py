import socket
import threading
import socketserver

import auth.TokenManager

from common.RequestStructures import MsgTypes, Message, MessageHeader

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port


class MasterChatServerHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        """
        Handles each new connection to the server.
        :return:
        """
        data = self.request.recv(50).strip()
        header = MessageHeader(0, MsgTypes.MSG_PASS, "").make_header()


def run_master_server(host=None, port=None):
    if host is None:
        host = HOST
    if port is None:
        port = PORT
    token_manager = auth.TokenManager.TokenManager("test_db")

    # Create the server, binding to host on port
    with socketserver.TCPServer((host, port), MasterChatServerHandler) as s:
        s.serve_forever()
