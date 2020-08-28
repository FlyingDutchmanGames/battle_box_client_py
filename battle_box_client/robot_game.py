import base64
from .client import Bot


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

class CommandsRequest:
    def __init__(self, commands_request, settings):
        self.player = commands_request["player"]
        self.turn = commands_request["turn"]
        self.turn = commands_request["turn"]

        robots = commands_request["game_state"]["robots"]

        self.my_robots = [Robot(robot, settings.terrain)
                for robot in robots if robot.player_id == player]
        self.enemy_robots = [Robot(robot, settings.terrain)
                for robot in robots if robot.player_id != player]

class Command:
    def __init__(self, robot, command_type, target=None):
        self.robot = robot
        self.command_type = command_type
        self.target = target

    def as_json(self):
        if self.command_type == "guard":
            return {"type": "guard", "robot_id": self.robot.id}
        elif self.command_type == "explode":
            return {"type": "explode", "robot_id": self.robot.id}
        elif self.command_type == "move":
            return {"type": "move", "robot_id": self.robot.id, "target": self.target}
        elif self.command_type == "attack":
            return {"type": "attack", "robot_id": self.robot.id, "target": self.target}


class Settings:
    def __init__(self, settings):
        self.explode_damage_min = settings["explode_damage_min"]
        self.explode_damage_max = settings["explode_damage_max"]
        self.collision_damage_min = settings["collision_damage_min"]
        self.collision_damage_max = settings["collision_damage_max"]
        self.attack_damage_min = settings["attack_damage_min"]
        self.attack_damage_max = settings["attack_damage_max"]
        self.max_turns = settings["max_turns"]
        self.robot_hp = settings["robot_hp"]
        self.spawn_every = settings["spawn_every"]
        self.spawn_per_player = settings["spawn_per_player"]
        self.terrain = Terrain(settings["terrain_base64"])

class Robot:
    def __init__(self, robot, terrain):
        self.terrain = terrain
        self.location = robot["location"]
        self.id = robot["id"]
        self.player_id = robot["player_id"]

    @property
    def adjacent_locations(self):
        [x, y] = self.location
        adjacent_locations = [
            [x + 1, y],
            [x - 1, y],
            [x, y + 1],
            [x, y - 1]
        ]
        return [
            location for location in adjacent_locations
            if 0 <= location[0] < self.terrain.cols
            and 0 <= location[1] < self.terrain.rows
        ]

    def manhattan_distance(self, target):
        return self.terrain.manhattan_distance(self.location, target)

    def guard(self):
        return Command(self, "guard")

    def explode(self):
        return Command(self, "explode")

    def move(self, target):
        return Command(self, "move", target=target)

    def move_towards(self, target):
        target = self.terrain.towards(self.location, target)
        return Command(self, "move", target=target)

    def attack(self, target):
        return Command(self, "attack", target=target)

    def __repr__(self):
        return f"Robot(id={self.id}, location={self.location}, player_id={self.player_id})"

class RobotGameBot(Bot):
    DEFAULT_ARENA = "robot-game-default"

    def post_process_commands(commands, settings):
        return [command.as_json() for command in commands]

    def process_game_request(self, game_request):
        return Settings(game_request)

    def process_commands_request(self, commands_request, settings):
        return CommandsRequest(commands_request, settings)
