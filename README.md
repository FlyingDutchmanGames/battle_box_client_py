# Battle Box Client (Python3)

## Getting Started

### Installation

```
pip3 install battle-box-client
```

### The Basics

botskrieg.com currently hosts the offical battlebox docs

[Getting Started Guide](https://botskrieg.com/docs/getting-started)

## Games

### RobotGame

[Checkout the example bots in this file](./battle_box_client/examples.py)

A basic robot game bot is any class that subclasses the `RobotGameBot` class and defined a `commands` method that takes three arguments. The following bot will return an

```python3
from battle_box_client import RobotGameBot

# Define your Bot

class MyBot(RobotGameBot):
  NAME = "my-bot"

  def commands(self, commands_request, settings):
    my_commands = []
    return my_commands

# Run your bot

bot = MyBot(token="{PUT YOUR TOKEN HERE (SEE GETTING STARTED GUIDE)}")

# Practice Matches
bot.practice() # Practice with random ai in default arena
bot.practice(arena="robot-game-default") # Run your bot in a specific arena
bot.practice(opponent="kansas") # Run your bot against a specific opponent

# Match Make Against Other User's Online Bots
bot.match_make() # match make in default arena
bot.match_make(arena="robot-game-default") # Match make in a specific arena
```

Once per turn your bot's `commands` method will be called with the `commands_request` and `settings` of the game, your method is expected to return a list of commands you'd like to send to the server

Inside the commands requests are the following fields [more details in official docs](https://botskrieg.com/docs/games/robot-game)

```python3
class MyBot(RobotGameBot):
  NAME = "my-bot"

  def commands(self, commands_request, settings):
    # commands_request has the following keys
    # commands_request.player <- Your player in this game (Integer)
    # commands_request.turn <- the turn this commands request is for (Integer)
    # commands_request["my_robots"] <- Your robots, instances of the RobotGameBot.Robot class
    # commands_request["enemy_robots"] <- Enemy robots, instances of the RobotGameBot.Robot class

    # settings has the following keys (see offical robot game docs for more details)
    # https://botskrieg.com/docs/games/robot-game
    # settings["attack_damage_max"]
    # settings["attack_damage_min"]
    # settings["collision_damage_max"]
    # settings["collision_damage_min"]
    # settings["explode_damage_max"]
    # settings["explode_damage_min"]
    # settings["max_turns"]
    # settings["robot_hp"]
    # settings["spawn_every"]
    # settings["spawn_per_player"]
    # settings["terrain"] <- An instance of the RobotGameBot.Terrain class
    return []
```

The `RobotGameBot.Terrain` class lets you do the following things
```python3
terrain.rows # number of rows in the terrain
terrain.cols # number of cols in the terrain
terrain.manhattan_distance(loc1, loc2) # manhattan distance between two locations
terrain.towards(loc1, loc2) # returns the next step loc1 can take in order to reach loc2
terrain.at_location(loc) # returns the type of terrain at a location is either ["inacessible", "normal", "spawn"]

```

The `RobotGameBot.Robot` class lets you do the following things
```python3
# Give information about the robot
robot.location # returns the [x, y] current location of the robot
robot.adjacent_locations # returns the adjacent [x, y] coordinates to the robot
robot.manhattan_distance(location) # returns the manhattan distance to the location https://en.wikipedia.org/wiki/Taxicab_geometry

# Create commands for the given robot
robot.guard() # returns a guard command for the robot
robot.explode() # returns a explode command for the robot
robot.attack(some_location) # returns an attack command towards the given location, the location must be an adjacent [x, y] coordinate
robot.move(some_location) # returns a move command towards the given location, the location must be an adjacent [x, y] coordinate
robot.move_towards(some_location) # returns a move command towards a given location, does *not* have to be adjacent
