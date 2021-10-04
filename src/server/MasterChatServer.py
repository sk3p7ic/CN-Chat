import socket
import threading
import socketserver

import server.db.DBManager as DBMgr
import server.auth.TokenManager as TokenMgr

from common.RequestStructures import MsgTypes, MessageHeader, decode_header

HOST = "127.0.0.1"  # Stores the default hostname
PORT = 42069  # Stores the default port

TOKEN_MANAGER = TokenMgr.TokenManager("test")


class MasterChatServerHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        """
        Handles each new connection to the server.
        :return:
        """
        data = decode_header(self.request.recv(50).strip())
        if len(data) == 0:
            header = MessageHeader(0, MsgTypes.MSG_FAIL,
                                   "Header not provided.").make_header()
        else:
            header = MessageHeader(0, MsgTypes.MSG_PASS, "").make_header()


def run_master_server(host=None, port=None):
    if host is None:
        host = HOST
    if port is None:
        port = PORT

    # Create the server, binding to host on port
    #with socketserver.TCPServer((host, port), MasterChatServerHandler) as s:
    #    s.serve_forever()
