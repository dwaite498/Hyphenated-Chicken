import json
import os
import time
from colony import Colony
from settings import MAP_WIDTH, MAP_HEIGHT, TICK_RATE

class Game:
    def __init__(self):
        self.time = time  # Alias for testing
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colony = Colony(2, 2)
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[2][2] = 'C'
        self.scout = None
        self.running = True
        self.last_tick = self.time.time()

    def run(self):
        print("Welcome to Planet Colonization!")
        self.render_map()
        while self.running:
            self.update()
            self.process_input()
            self.time.sleep(0.1)

    def update(self):
        current_time = self.time.time()
        if current_time - self.last_tick >= TICK_RATE:
            self.colony.update()
            self.last_tick = current_time
            self.render_map()

    def render_map(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"Metal: {self.colony.metal}")
        if self.scout:
            self.fog[self.scout.y][self.scout.x] = "S"  # Show scout position
        for row in self.fog:
            print(" ".join(row))
        print("\nCommands: build scout, move <north/south/east/west>, quit")

    def process_input(self):
        try:
            command = input("> ").strip().lower().split()
            if not command:
                return
            if command[0] == "quit":
                self.running = False
                print("Leaving the planet...")
            elif command[0] == "build" and len(command) > 1 and command[1] == "scout":
                if not self.scout:
                    self.scout = self.colony.build_scout()
                    if self.scout:
                        print("Scout built!")
                    else:
                        print("Need 5 metal to build a scout!")
                else:
                    print("Only one scout allowed for now!")
            elif command[0] == "move" and len(command) > 1 and self.scout:
                direction = command[1]
                if self.scout.move(direction, self):
                    print(f"Scout moved {direction}.")
                else:
                    print("Can't move that way!")
            else:
                print("Invalid command!")
        except EOFError:
            pass
