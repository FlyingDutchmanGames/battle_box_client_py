import urllib.parse
import json
import os
import socket
import ssl
import struct
import time
import base64

class BattleBoxError(Exception):
    pass

# LOAD SETTINGS
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
        self.socket = socket.create_connection((parsed_uri.hostname, parsed_uri.port))

        if parsed_uri.scheme in ["battleboxs", "https"]:
            context = ssl.create_default_context()
            self.socket = context.wrap_socket(self.socket, server_hostname=parsed_uri.hostname)

        self.send_message({'token': token, "bot": bot})
        connection_msg = self.receive_message()

        if connection_msg.get("error"):
            raise ValueError(connection_msg)
        else:
            self.bot_server_id = connection_msg["bot_server_id"]

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
    NAME="unnamed"

    def __init__(self, **options):
        self.uri = options.get("uri", "battleboxs://botskrieg.com:4242")
        hostname = urllib.parse.urlparse(self.uri).hostname
        self.token = options.get("token") or load_token(hostname)
        self.bot = self.NAME
        self.connection = options.get("connection") or BattleBoxConnection()
        self.connection.connect(self.uri, self.token, self.bot)

    def accept_game(self, game_request):
        game_id = game_request["game_info"]["game_id"]
        self.connection.send_message({"action": "accept_game", "game_id": game_id})

    def play(self, game_request):
        game_request = self.process_game_request(game_request)

        while True:
            msg = self.connection.receive_message()
            if msg.get("commands_request"):
                commands_request = self.process_commands_request(msg["commands_request"])
                commands = self.commands(commands_request, game_request)
                self.send_commands(msg["commands_request"]["request_id"], commands)
            elif msg.get("error") == "invalid_commands_submission":
                print("Failed to send commands in time for request_id: {}".format(msg["request_id"]))
            elif msg.get("info"):
                if msg["info"] == "game_over":
                    print(msg["result"])

                break


    def send_commands(self, request_id, commands):
        self.connection.send_message({"action": "send_commands", "request_id": request_id, "commands": commands})

    def practice(self, **options):
        arena = options.get("arena", self.DEFAULT_ARENA)
        opponent = options.get("opponent", {})
        self.connection.send_message({"action": "practice", "opponent": opponent, "arena": arena})
        status = self.connection.receive_message()
        if status.get("error"):
            raise BattleBoxError(status["error"])
        assert status["status"] == "match_making"
        game_request = self.connection.receive_message()
        self.accept_game(game_request)
        self.play(game_request)


class RobotGameBot(Bot):
    DEFAULT_ARENA = "robot-game-default"

    class Robot:
        def __init__(self, robot):
            self.location = robot["location"]
            self.id = robot["id"]
            self.player_id = robot["player_id"]

        def guard(self):
            return {"type": "guard", "robot_id": self.id}

        def explode(self):
            return {"type": "explode", "robot_id": self.id}

        def move(self, target):
            return {"type": "move", "robot_id": self.id, "target": target}

        def attack(self, target):
            return {"type": "attack", "robot_id": self.id, "target": target}

        def __repr__(self):
            return f"Robot(id={self.id}, location={self.location}, player_id={self.player_id})"

    class Terrain:
        def __init__(self, terrain_base64):
            terrain = base64.b64decode(terrain_base64)
            self.rows = terrain[0]
            self.cols = terrain[1]
            self.terrain_data = terrain[2:]

        def manhattan_distance(self, loc1, loc2):
            [x1, y1] = loc1
            [x2, y2] = loc2
            a_squared = (x2 - x1) ** 2
            b_squared = (y2 - y1) ** 2
            return (a_squared + b_squared) ** 0.5

        def towards(self, loc1, loc2):
            [x1, y1] = loc1
            [x2, y2] = loc2

            if x1 > x2:
              return [x1 - 1, y1]

            elif x1 < x2:
              return [x1 + 1, y1]

            elif y1 > y2:
              return [x1, y1 - 1]

            elif y1 < y2:
              return [x1, y1 + 1]

            else:
              return [x1, y1]

        def at_location(self, location):
            [x, y] = location
            if (x not in range(self.cols)) or (y not in range(self.rows)):
                return "inacessible"
            else:
                offset = x + (y * self.cols) 
                terrain_type = self.terrain_data[offset]
                return {
                    0: "inacessible",
                    1: "normal",
                    2: "spawn"
                }[terrain_type]

        def __repr__(self):
            return f"Terrain(rows={self.rows}, cols={self.cols})"


    def process_game_request(self, game_request):
        settings = game_request["game_info"]["settings"]
        settings["terrain"] = self.Terrain(settings["terrain_base64"])
        return settings

    def process_commands_request(self, commands_request):
        player = commands_request["player"]
        robots = commands_request["game_state"]["robots"]
        my_robots = [self.Robot(robot) for robot in robots if robot["player_id"] == player]
        enemy_robots = [self.Robot(robot) for robot in robots if robot["player_id"] != player]
        return {
            "player": player,
            "robots": robots,
            "my_robots": my_robots,
            "enemy_robots": enemy_robots,
            "turn": commands_request["game_state"]["turn"]
        }

class Tortuga(RobotGameBot):
    NAME = "tortuga"

    def commands(self, commands_request, settings):
        return [robot.guard() for robot in commands_request["my_robots"]]

