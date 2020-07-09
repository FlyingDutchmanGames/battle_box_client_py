from client import RobotGameBot

class Tortuga(RobotGameBot):
    NAME = "tortuga"

    def commands(self, commands_request, settings):
        return [robot.guard() for robot in commands_request["my_robots"]]
