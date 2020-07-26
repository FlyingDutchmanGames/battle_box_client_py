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

        commands = []

        for robot in commands_request["my_robots"]:
            [x, y] = robot.location

            if y > row_midpoint:
                commands.append(robot.move([x, y - 1]))
            elif y < row_midpoint:
                commands.append(robot.move([x, y + 1]))
            elif x > col_midpoint:
                commands.append(robot.move([x - 1, y]))
            else:
                commands.append(robot.move([x + 1, y]))

        return commands


class HoneyBadger(RobotGameBot):
    NAME = "honey-badger"

    def commands(self, commands_request, settings):
        commands = []

        for robot in commands_request["my_robots"]:
            adjacent_enemies = [
                enemy for enemy in commands_request["enemy_robots"]
                if enemy.location in robot.adjacent_locations
            ]

            if adjacent_enemies:
                target = adjacent_enemies[0].location
                command = robot.attack(target)
            elif commands_request["enemy_robots"]:
                closest_enemy = min(commands_request["enemy_robots"], key=lambda enemy: robot.manhattan_distance(enemy.location))
                command = robot.move_towards(closest_enemy.location)
            else:
                command = robot.guard()

            commands.append(command)

        return commands
