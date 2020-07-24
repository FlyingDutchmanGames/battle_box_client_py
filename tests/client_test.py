import unittest
import base64
from battle_box_client import *

class FakeConnection:
    def __init__(self, **options):
        self.received_messages = options.get("received_messages") or []
        self.received_messages.reverse()
        self.sent_messages = []

    def connect(self, uri, key, bot):
        self.uri = uri
        self.key = key
        self.bot = bot

    def send_message(self, message):
        self.sent_messages.append(message)

    def receive_message(self):
        return self.received_messages.pop()

class BotTest(unittest.TestCase):
    def test_connect(self):
        fake_connection = FakeConnection(received_messages=[
            {"status": "match_making"},
            {
                "game_info": {
                    "game_id": "{some uuid}",
                    "player": 1,
                    "settings": {
                        "terrain_base64": b'AgIAAQIA'
                    }
                },
                "game_type": "robot_game",
                "request_type": "game_request"
            },
            {
                "info": "game_over",
                "result": {
                    "game_id": "{game_id}",
                    "score": {
                        "1": 10,
                        "2": 4,
                    }
                }
            }
        ])
        bot = RobotGameBot(connection=fake_connection)
        bot.practice()
        self.assertEqual(fake_connection.sent_messages, [
            {'action': 'practice', 'arena': 'robot-game-default', 'opponent': {}},
            {'action': 'accept_game', 'game_id': '{some uuid}'}
        ])

    def test_practice_match_errors(self):
        practice_errors = [
            {"error":{"arena":["Arena \"some-arena\" does not exist"]}},
            {"error":{"opponent":["No opponent matching ({\"difficulty\":{\"min\":2},\"name\":\"not-real-opponent\"})"]}}
        ]

        for error in practice_errors:
            fake_connection = FakeConnection(received_messages=[{"error": error}])
            bot = RobotGameBot(connection=fake_connection)

            with self.assertRaises(BattleBoxError):
                bot.practice()

            self.assertEqual(fake_connection.sent_messages, [
                {'action': 'practice', 'arena': 'robot-game-default', 'opponent': {}},
            ])

    def test_auth_errors(self):
        auth_errors = [
            {"token":["Invalid API Key"]},
            {"user":["User is banned"]},
            {"user":["User connection limit exceeded"]},
            {"bot":{"name":["Can only contain alphanumeric characters or hyphens"]}},
            {"bot":{"name":["should be at most 39 character(s)"]}},
            {"bot":{"name":["Cannot end with a hyphen"]}},
            {"bot":{"name":["Cannot start with a hyphen"]}},
            {"bot":{"name":["Cannot contain two hyphens in a row"]}},
        ]

        for error in auth_errors:
            fake_connection = FakeConnection(received_messages=[{"error": error}])
            bot = RobotGameBot(connection=fake_connection)

            with self.assertRaises(BattleBoxError):
                bot.practice()

            self.assertEqual(fake_connection.sent_messages, [
                {'action': 'practice', 'arena': 'robot-game-default', 'opponent': {}},
            ])


class RobotGameRobotTest(unittest.TestCase):
    def test_moves(self):
        robot = RobotGameBot.Robot({"id": 1, "player_id": 1, "location": [1, 1]})
        self.assertEqual({'robot_id': 1, 'type': 'guard'}, robot.guard())
        self.assertEqual({'robot_id': 1, 'type': 'explode'}, robot.explode())
        self.assertEqual({'robot_id': 1, 'target': [1, 1], 'type': 'move'}, robot.move([1,1]))
        self.assertEqual({'robot_id': 1, 'target': [1, 1], 'type': 'attack'}, robot.attack([1,1]))

class RobotGameTerrainTest(unittest.TestCase):
    def test_at(self):
        terrain_base64 = base64.b64encode(bytes([2, 2, 0, 1, 2, 0]))
        terrain = RobotGameBot.Terrain(terrain_base64)
        self.assertEqual(terrain.at([0, 0]), "inacessible")
        self.assertEqual(terrain.at([1, 0]), "spawn")
        self.assertEqual(terrain.at([0, 1]), "normal")

if __name__ == '__main__':
    unittest.main()
