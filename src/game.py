import json
from player import Player

class Game:
    def __init__(self):
        self.player = Player()
        with open("../data/rooms.json", "r") as f:
            self.rooms = json.load(f)
        self.running = True

    def run(self):
        print("Welcome to the Adventure!")
        self.describe_room()
        while self.running:
            command = input("> ").strip().lower().split()
            self.process_command(command)

    def describe_room(self):
        room = self.rooms[self.player.location]
        print(f"\nYou are in the {self.player.location}.")
        print(room["description"])
        if "items" in room:
            print("Items here:", ", ".join(room["items"]))
        print("Exits:", ", ".join(room["exits"].keys()))

    def process_command(self, command):
        if not command:
            return
        action = command[0]
        if action == "quit":
            self.running = False
            print("Goodbye!")
        elif action == "go" and len(command) > 1:
            direction = command[1]
            room = self.rooms[self.player.location]
            if direction in room["exits"]:
                self.player.move(room["exits"][direction])
                self.describe_room()
            else:
                print("You can't go that way!")
        elif action == "take" and len(command) > 1:
            item = command[1]
            room = self.rooms[self.player.location]
            if "items" in room and item in room["items"]:
                self.player.take(item)
                room["items"].remove(item)
            else:
                print("No such item here!")
        else:
            print("Commands: go <direction>, take <item>, quit")