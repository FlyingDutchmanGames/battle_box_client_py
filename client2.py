import urllib.parse
import json
import os
import socket
import ssl
import struct
import time

# LOAD SETTINGS
LOAD_KEY_ERROR_MSG = """
Unable to laod api key, this client support the following ways to load a key
1.) Passing the BATTLE_BOX_API_KEY environment variable
2.) Creating a file in the current directory named `./.battle_box` in the following format
```
{"botskrieg.com": {"token": "YOUR_TOKEN_HERE"}}
```
"""

def load_key(domain):
    env = os.environ.get('BATTLE_BOX_API_KEY')
    if env:
        return env
    elif os.path.isfile("./.battle_box"):
        with open("./.battle_box") as file:
            data = file.read()
            return json.loads(data)[domain]["token"]
    else:
        raise ValueError(LOAD_KEY_ERROR_MSG)


# WIRE PROTOCOL

class BattleBoxConnection:
    def __init__(self, uri, key, arena, bot):
        parsed_uri = urllib.parse.urlparse(uri)
        self.socket = socket.create_connection((parsed_uri.hostname, parsed_uri.port))
        context = ssl.create_default_context()
        self.socket = context.wrap_socket(self.socket, server_hostname=parsed_uri.hostname)
        self.send_message({'token': key, 'arena': arena, "bot": bot})
        connection_msg = self.recieve_message()
        if connection_msg.get("error"):
            raise ValueError(connection_msg)
        else:
            self.bot_server_id = connection_msg["bot_server_id"]

    def send_message(self, msg):
        msg_bytes = str.encode(json.dumps(msg))
        header = struct.pack("!H", len(msg_bytes))
        self.socket.sendall(header + msg_bytes)

    def recieve_message(self):
        msg_size_bytes = self.socket.recv(2)
        (msg_size,) = struct.unpack("!H", msg_size_bytes)
        message = self.socket.recv(msg_size)
        message = json.loads(message)
        return message

# BOTS

class Bot:
    NAME="unnamed"

    def __init__(self, **options):
        self.uri = options.get("uri", "battlebox://botskrieg.com:4242")
        hostname = urllib.parse.urlparse(self.uri).hostname
        self.key = load_key(hostname)
        self.bot = self.NAME
        self.arena = options.get("arena", self.DEFAULT_ARENA)
        self.connection = BattleBoxConnection(self.uri, self.key, self.arena, self.bot)

    def accept_game(self, game_request):
        game_id = game_request["game_info"]["game_id"]
        self.connection.send_message({"action": "accept_game", "game_id": game_id})

    def send_commands(self, request_id, commands):
        self.connection.send_message({"action": "send_commands", "request_id": request_id, "commands": commands})

    def practice(self, opponent={}):
        self.connection.send_message({"action": "practice", "opponent": opponent})
        status = self.connection.recieve_message()
        assert status["status"] == "match_making"
        game_request = self.connection.recieve_message()
        self.accept_game(game_request)
        self.play(game_request)


class RobotGameBot(Bot):
    DEFAULT_ARENA = "robot-game-default"

    def play(self, game_request):
        while True:
            msg = self.connection.recieve_message()
            if msg.get("commands_request"):
                commands = self.commands(
                    msg["commands_request"],
                    game_request["game_info"]["player"],
                    game_request["game_info"]["settings"]
                )
                self.send_commands(msg["commands_request"]["request_id"], commands)
            elif msg.get("info"):
                if msg["info"] == "game_over":
                    print(msg["result"])

                break


class ShelterInPlace(RobotGameBot):
    NAME = "shelter-in-place"

    def commands(self, commands_request, player, game_request):
        print(commands_request)
        print(player)
        print(game_request)
        return []
