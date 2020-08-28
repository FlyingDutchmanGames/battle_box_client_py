import urllib.parse
import json
import os
import socket
import ssl
import struct
import time


class BattleBoxError(Exception):
    pass

def load_token(domain):
    env = os.environ.get('BATTLE_BOX_API_TOKEN')
    if env:
        return env
    elif os.path.isfile("./.battle_box"):
        with open("./.battle_box") as file:
            data = file.read()
            return json.loads(data)[domain]["token"]


class BattleBoxConnection:
    def connect(self, uri, token, bot):
        parsed_uri = urllib.parse.urlparse(uri)
        self.socket = socket.create_connection(
            (parsed_uri.hostname, parsed_uri.port))

        if parsed_uri.scheme in ["battleboxs", "https"]:
            context = ssl.create_default_context()
            self.socket = context.wrap_socket(
                self.socket, server_hostname=parsed_uri.hostname)

        self.send_message({'token': token, "bot": bot})
        connection_msg = self.receive_message()

        if connection_msg.get("error"):
            raise ValueError(connection_msg)
        else:
            self.bot_server_id = connection_msg["bot_server_id"]
            print("Watch your bot here! ", connection_msg["watch"]["bot"])

    def send_message(self, msg):
        msg_bytes = str.encode(json.dumps(msg))
        header = struct.pack("!H", len(msg_bytes))
        self.socket.sendall(header + msg_bytes)

    def receive_message(self):
        msg_size_bytes = self.socket.recv(2)
        (msg_size,) = struct.unpack("!H", msg_size_bytes)
        message = self.socket.recv(msg_size)
        message = json.loads(message)
        return message


class Bot:
    NAME = "unnamed"

    def __init__(self, **options):
        self.uri = options.get("uri", "battleboxs://botskrieg.com:4242")
        hostname = urllib.parse.urlparse(self.uri).hostname
        self.token = options.get("token") or load_token(hostname)
        self.bot = self.NAME
        self.connection = options.get("connection") or BattleBoxConnection()
        self.connection.connect(self.uri, self.token, self.bot)

    def accept_game(self, game_request):
        game_id = game_request["game_info"]["game_id"]
        self.connection.send_message(
            {"action": "accept_game", "game_id": game_id})

    def play(self, game_request):
        game_request = self.process_game_request(game_request)

        while True:
            msg = self.connection.receive_message()
            if msg.get("commands_request"):
                commands_request = self.process_commands_request(
                    msg["commands_request"])
                commands = self.commands(commands_request, game_request)
                commands = self.post_process_commands(commands)
                self.send_commands(
                    msg["commands_request"]["request_id"], commands)
            elif msg.get("error") == "invalid_commands_submission":
                print(
                    "Failed to send commands in time for request_id: {}".format(
                        msg["request_id"]))
            elif msg.get("info"):
                if msg["info"] == "game_over":
                    print(msg["result"])

                break

    def send_commands(self, request_id, commands):
        self.connection.send_message(
            {"action": "send_commands", "request_id": request_id, "commands": commands})

    def match_make(self, **options):
        arena = options.get("arena", self.DEFAULT_ARENA)
        self.connection.send_message(
            {"action": "start_match_making", "arena": arena})
        status = self.connection.receive_message()
        if status.get("error"):
            raise BattleBoxError(status["error"])
        assert status["status"] == "match_making"
        game_request = self.connection.receive_message()
        self.accept_game(game_request)
        self.play(game_request)

    def practice(self, **options):
        arena = options.get("arena", self.DEFAULT_ARENA)
        opponent = options.get("opponent", {})
        self.connection.send_message(
            {"action": "practice", "opponent": opponent, "arena": arena})
        status = self.connection.receive_message()
        if status.get("error"):
            raise BattleBoxError(status["error"])
        assert status["status"] == "match_making"
        game_request = self.connection.receive_message()
        self.accept_game(game_request)
        self.play(game_request)


