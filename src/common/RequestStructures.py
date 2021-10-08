from dataclasses import dataclass
from enum import Enum
import json


class MsgTypes(Enum):
    MSG_NAME = 0
    MSG_NORM = 1
    MSG_FILE = 2
    MSG_PASS = 3
    MSG_FAIL = 4


def get_type_from_str(string: str) -> MsgTypes:
    """
    Gets a message type from a given message type name.
    :param string: A string of the name of a type in MsgTypes.
    :return: MsgTypes.
    """
    for msg_type in MsgTypes:
        if string == msg_type.name:
            return msg_type
    raise ValueError(f"[E] Value, {string}, not found in MsgTypes...")


@dataclass(frozen=True)
class Message:
    user_id: int  # The ID of the user that is sending the message
    message: bytes  # The data of the message itself
    msg_type: MsgTypes  # The type of the message

    def get_json(self) -> str:
        """
        Gets a JSON-formatted string from the data stored in this class.
        :return: str.
        """
        return json.dumps({"user_id": self.user_id, "message": self.message.decode("utf8"),
                           "msg_type": self.msg_type.name})


def get_message_from_json(json_msg: [str, bytes]) -> Message:
    """
    Reads a given message in json format and returns a Message object with that data.
    :param json_msg: The message, either in type str or bytes and formatted as a json string, that will be read.
    :return: Message object containing the given data.
    """
    # Decode the message if it is passed as type "bytes"
    if type(json_msg) is bytes:
        json_msg = json_msg.decode("utf8")
    json_data = json.loads(json_msg)  # Read the JSON string and parse into dict
    # Ensure that the fields we need are in the supplied date
    if "user_id" not in json_data.keys() or "message" not in json_data.keys() or "msg_type" not in json_data.keys():
        raise ValueError(f"[E] Needed data types missing in {json_data}")
    else:
        return Message(json_data["user_id"], json_data["message"], get_type_from_str(json_data["msg_type"]))
