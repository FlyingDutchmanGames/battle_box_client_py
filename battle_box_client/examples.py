from .client import RobotGameBot

class Tortuga(RobotGameBot):
    NAME = "tortuga"

    def commands(self, commands_request, settings):
        return [robot.guard() for robot in commands_request["my_robots"]]

class Kansas(RobotGameBot):
    NAME = "kansas"

    def commands(self, commands_request, settings):
        row_midpoint = settings["terrain"].rows // 2
        col_midpoint = settings["terrain"].cols // 2

        moves = []

        for robot in commands_request["my_robots"]:
            [x, y] = robot.location

            if y > row_midpoint:
                moves.append(robot.move([x, y - 1]))
            elif y < row_midpoint:
                moves.append(robot.move([x, y + 1]))
            elif x > col_midpoint:
                moves.append(robot.move([x - 1, y]))
            else:
                moves.append(robot.move([x + 1, y]))

        return moves
