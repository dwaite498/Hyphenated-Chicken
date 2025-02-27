import json
import os
import time
from colony import Colony
from settings import MAP_WIDTH, MAP_HEIGHT, TICK_RATE

class Game:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colony = Colony(2, 2)  # Starting position
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[2][2] = 'C'  # Reveal colony tile
        self.running = True
        self.last_tick = time.time()

    def run(self):
        print("Welcome to Planet Colonization!")
        self.render_map()
        while self.running:
            self.update()
            self.process_input()
            time.sleep(0.1)  # Light sleep to prevent CPU hogging

    def update(self):
        current_time = time.time()
        if current_time - self.last_tick >= TICK_RATE:
            self.colony.update()
            self.last_tick = current_time
            self.render_map()

    def render_map(self):
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear console
        print(f"Metal: {self.colony.metal}")
        for row in self.fog:
            print(" ".join(row))
        print("\nCommands: quit")

    def process_input(self):
        try:
            command = input("> ").strip().lower()
            if command == "quit":
                self.running = False
                print("Leaving the planet...")
        except EOFError:
            pass  # Ignore Ctrl+D in Gitpod
