#!/usr/bin/env python3

import socket
import json
import struct
import ssl

# Constants
TOKEN = 'insert-my-token-here'
LOBBY = 'robot_game:practice'
HOST = 'app.botskrieg.com'
PORT = 4242

# Wire Protocol
def send_message(socket, msg):
    msg_bytes = str.encode(json.dumps(msg))
    header = struct.pack("!H", len(msg_bytes))
    socket.sendall(header + msg_bytes)

def recieve_message(socket):
    msg_size_bytes = socket.recv(2)
    (msg_size,) = struct.unpack("!H", msg_size_bytes)
    message = socket.recv(msg_size)
    return json.loads(message)

def start_match_making_msg():
    return {'action': 'start_match_making'}

def accept_game_msg(game_id):
    return {"action": "accept_game", "game_id": game_id}

def send_commands_msg(request_id,commands):
    return {"action": "send_commands", "request_id": request_id, "commands": commands}

def create_guard(robot_id):
    return {"type": "guard", "robot_id": robot_id}

def create_suicide(robot_id):
    return {"type": "suicide", "robot_id": robot_id}

def create_move(robot_id, target):
    return {"type": "move", "robot_id": robot_id, "target": target}

def create_attack(robot_id, target):
    return {"type": "attack", "robot_id": robot_id, "target": target}

# Connect to the server
context = ssl.create_default_context()
connection = socket.create_connection((HOST, PORT))
socket = context.wrap_socket(connection, server_hostname=HOST)

# Authenticate to the server
send_message(socket, {'token': TOKEN, 'lobby': LOBBY})
connection_message = recieve_message(socket)
#print(connection_message)
bot_server_id = connection_message["bot_server_id"]
watch_bot_url = f"https://app.botskrieg.com/bot_servers/{bot_server_id}/follow"
print("WATCH URL:", watch_bot_url)

# This "while loop" starts a new game after previous... forever
while True:

    # Request to begin match making
    send_message(socket, start_match_making_msg())
    status = recieve_message(socket)
    print("Status:", status["status"])

    game_info = recieve_message(socket)
    print("Game Starting")
    #print("Recieved Request:", game_info["request_type"])
    #print("game_id:", game_info["game_info"]["game_id"])
    player = game_info["game_info"]["player"]
    turns = game_info["game_info"]["settings"]["max_turns"]
    send_message(socket, accept_game_msg(game_info["game_info"]["game_id"]))
    #print(game_info)

    # This "for loop" is the section that will be called each turn
    for turn in range(0, turns):
        command_request = recieve_message(socket)
        # Create an emtpy array that will be filled with commands that are created
        commands = []
        #print(command_request)
        # Define all robots
        robots = command_request['commands_request']['game_state']['robots']
        # Specify which of the robots are mine
        my_robots = [robot for robot in robots if robot['player_id'] == player]
            
        # This "for loop" will run for each individual robot I control
        for robot in my_robots:
            # Specifiy where a robot is
            [row,column] = robot["location"]
            # Define the command for each robot
            target = [row+1, column]
            command = create_move(robot['id'], target)

            # Add this command to the array of commands you will be sending
            commands.append(command)
            # Print the turn and command information on the console
            #print("TURN:", turn,"COMMAND:", command)

        # Send commands to the server
        msg = send_commands_msg(command_request['commands_request']['request_id'], commands)
        send_message(socket, msg)

    game_result = recieve_message(socket)
    print("Game Over:", game_result["info"])
    print("Result: ", game_result["result"]["score"])