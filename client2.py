from urllib.parse import urlparse
import json
import os

LOAD_KEY_ERROR_MSG = """
Unable to laod api key, this client support the following ways to load a key
1.) Passing the BATTLE_BOX_API_KEY environment variable
2.) Creating a file in the current directory named `./.battle_box` in the following format
```
{"botskrieg.com": {"token": "YOUR_TOKEN_HERE"}}
```
"""

def load_key(domain):
    env = os.environ.get('BATTLE_BOX_API_KEY')
    if env:
        return env
    elif os.path.isfile("./.battle_box"):
        with open("./.battle_box") as file:
            data = file.read()
            return json.loads(data)[domain]["token"]
    else:
        raise ValueError(LOAD_KEY_ERROR_MSG)

def send_message(socket, msg):
    msg_bytes = str.encode(json.dumps(msg))
    header = struct.pack("!H", len(msg_bytes))
    socket.sendall(header + msg_bytes)

def recieve_message(socket):
    msg_size_bytes = socket.recv(2)
    (msg_size,) = struct.unpack("!H", msg_size_bytes)
    message = socket.recv(msg_size)
    return json.loads(message)

def parse(uri):
    parsed = urlparse(uri)
    return parsed

class Bot:
    def __init__(self, **options):
        self.target = parse(options.get("uri", "battlebox://botskrieg.com:4242"))
        self.key = load_key(self.target.hostname)
        self.arena = options.get("arena", self.DEFAULT_ARENA)

class RobotGameBot(Bot):
    DEFAULT_ARENA = "robot_game:default"
