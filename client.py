#!/usr/bin/env python3

import socket
import json
import struct
import ssl

TOKEN = '4egpgtuomne65bs3yk7mqxosadhf2sid'
LOBBY = 'robot_game:practice'
HOST = b'app.botskrieg.com'
PORT = 4242

def send_message(socket, msg):
    msg_bytes = str.encode(json.dumps(msg))
    header = struct.pack("!H", len(msg_bytes))
    socket.sendall(header + msg_bytes)

def recieve_message(socket):
    msg_size_bytes = socket.recv(2)
    (msg_size,) = struct.unpack("!H", msg_size_bytes)
    message = socket.recv(msg_size)
    return message

context = ssl.create_default_context()

connection = socket.create_connection((HOST, PORT))
socket = context.wrap_socket(connection, server_hostname=HOST)

send_message(socket, {'token': TOKEN, 'lobby': LOBBY})
msg = recieve_message(socket)
connection_message = json.loads(msg)
print(repr(connection_message))
print("connection_id:", connection_message["connection_id"])

send_message(socket, {'action': 'start_match_making'})
msg = recieve_message(socket)
status = json.loads(msg)
print("status:", status["status"])

msg = recieve_message(socket)
decoded = json.loads(msg)
print("Recieved Request:", decoded["request_type"])
print("game_id:", decoded["game_info"]["game_id"])
print("player:", decoded["game_info"]["player"])

send_message(socket, {"action": "accept_game", "game_id": decoded["game_info"]["game_id"]})

for i in range(0, 100):
    msg = recieve_message(socket)
    decoded = json.loads(msg)
    print(i, ": Recieved Request:", decoded["request_type"], "commands_request_id", decoded["commands_request"]["request_id"])
    send_message(socket, {"action": "send_commands", "request_id": decoded["commands_request"]["request_id"], "commands": []})

msg = recieve_message(socket)
decoded = json.loads(msg)
print("Game Over:", decoded["info"])
print("Result: ", decoded["result"]["score"])


