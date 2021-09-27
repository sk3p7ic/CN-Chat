from enum import Enum
import socket
import os


class MsgTypes(Enum):
    MSG_NAME = 0
    MSG_NORM = 1
    MSG_FILE = 2
    MSG_PASS = 3
    MSG_FAIL = 4


class MessageHeader:
    @staticmethod
    def get_msg_size(msg_type: MsgTypes, msg: str) -> int:
        """
        Gets the size of the message based odd of the message type.
        :param msg_type: The type of the message.
        :param msg: The message, as a string either containing the message or
        the path to the file that will be sent as the message.
        :return: Either the length of the string being sent as a message or the
        size of the file being sent as a message.
        """
        if msg_type == MsgTypes.MSG_NAME or msg_type == MsgTypes.MSG_NORM:
            return len(msg)
        elif msg_type == MsgTypes.MSG_FILE:
            return os.stat(msg).st_size

    def __init__(self, user_id, msg_type, msg):
        self.user_id = str(user_id).zfill(4)
        self.msg_type = msg_type
        try:
            self.msg_len = self.get_msg_size(msg_type, msg)
        except OSError as err:
            raise Exception(f"[!] Encountered an error!\n\t{err}")

    def make_header(self):
        """
        Creates a properly-formatted message header.
        :return: The message header.
        """
        header = f"User-ID: {self.user_id}\n"
        header += f"Msg-Type: {self.msg_type.name}\n"
        header += f"Msg-Length: {str(self.msg_len).zfill(4)}\n"
        if len(header) != 50:
            raise Exception("[!] An error occurred generating the header"
                            "(header length: {})".format(len(header)))
        else:
            return header.encode()


class Message:
    def __init__(self, user_id, msg_type, msg):
        if msg_type == MsgTypes.MSG_FILE:
            path = os.path.realpath(msg)
            self.header = MessageHeader(user_id, msg_type, path).make_header()
        else:
            self.header = MessageHeader(user_id, msg_type, msg).make_header()
        self.msg = msg

    def transfer_msg(self, conn: socket):
        def send_and_verify(msg: [str, bytes]):
            # Ensure that the message is encoded so that it may be sent
            if type(msg) is not bytes:
                msg = msg.encode()
            conn.sendAll(msg)
            resp = conn.recv(50).decode()
            if "MSG_PASS" not in resp:
                raise Exception(f"[!] Error in response:\n{resp}")
            return resp

        header_resp = send_and_verify(self.header)
        msg_resp = send_and_verify(self.msg)
        return header_resp, msg_resp

