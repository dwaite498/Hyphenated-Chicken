import json
import os
import time
import pygame
from colony import Colony
import unit
import rendering
import movement
import combat
from settings import MAP_WIDTH, MAP_HEIGHT, WINDOW_SIZE

class Game:
    def __init__(self):
        pygame.init()
        self.time = time
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Planet Colonization")
        self.clock = pygame.time.Clock()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colonies = [Colony(4, 4)]  # Center at (4, 4)
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[4][4] = 'C'
        # Initial 1-tile vision around colony
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x, y = 4 + dx, 4 + dy
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    if [x, y] in self.planet["resources"]["metal"]:
                        self.fog[y][x] = "M"
                    elif [x, y] in self.planet["enemies"]:
                        self.fog[y][x] = "E"
                    else:
                        self.fog[y][x] = self.planet["tiles"][y][x]
        self.scouts = []
        self.constructors = []
        self.enemies = [unit.Enemy(x, y) for x, y in self.planet["enemies"]]
        self.selected = []
        self.running = True
        self.paused = False
        self.game_started = False
        self.game_over = False
        self.last_metal_tick = self.time.time()
        self.last_combat_tick = self.time.time()
        self.show_guide = False
        self.show_build_menu = False
        self.debug = False

    def reset_game(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colonies = [Colony(4, 4)]
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x, y = 4 + dx, 4 + dy
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    if [x, y] in self.planet["resources"]["metal"]:
                        self.fog[y][x] = "M"
                    elif [x, y] in self.planet["enemies"]:
                        self.fog[y][x] = "E"
                    else:
                        self.fog[y][x] = self.planet["tiles"][y][x]
        self.scouts = []
        self.constructors = []
        self.enemies = [unit.Enemy(x, y) for x, y in self.planet["enemies"]]
        self.selected = []
        self.paused = False
        self.game_started = False
        self.game_over = False
        self.last_metal_tick = self.time.time()
        self.last_combat_tick = self.time.time()
        self.show_guide = False
        self.show_build_menu = False

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_started and not self.paused and not self.game_over:
                self.update()
            rendering.render(self)
            self.clock.tick(60)

    def update(self):
        movement.update(self)
        combat.update(self)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_d:
                    self.debug = not self.debug
                    print(f"Debug mode: {self.debug}")
                elif event.key == pygame.K_b and self.colonies and any(c in self.selected for c in self.colonies):
                    self.show_build_menu = not self.show_build_menu
                    self.show_guide = False
                    if self.debug:
                        print(f"Build menu toggled via B: {self.show_build_menu}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                if event.button == 1:
                    # Button checks first
                    if 620 <= event.pos[0] <= 700:
                        if 540 <= event.pos[1] <= 570:  # Guide button
                            self.show_guide = not self.show_guide
                            self.show_build_menu = False
                            if self.debug:
                                print(f"Guide toggled: {self.show_guide}")
                        elif 500 <= event.pos[1] <= 530 and self.colonies and any(c in self.selected for c in self.colonies):  # Build button
                            self.show_build_menu = not self.show_build_menu
                            self.show_guide = False
                            if self.debug:
                                print(f"Build menu toggled: {self.show_build_menu}")
                        elif 460 <= event.pos[1] <= 490 and self.game_started and not self.game_over:  # Restart button
                            self.reset_game()
                            if self.debug:
                                print("Game restarted from playfield")
                    guide_active = self.show_guide and 350 <= event.pos[0] <= 450 and 500 <= event.pos[1] <= 540
                    # Build menu options
                    if self.show_build_menu and self.colonies and any(c in self.selected for c in self.colonies):
                        if 610 <= event.pos[0] <= 710:
                            if 200 <= event.pos[1] <= 230:
                                new_scout = self.colonies[0].build_scout()
                                if new_scout:
                                    self.scouts.append(new_scout)
                                    if self.debug:
                                        print(f"Built scout, total: {len(self.scouts)}")
                            elif 240 <= event.pos[1] <= 270:
                                new_constructor = self.colonies[0].build_constructor()
                                if new_constructor:
                                    self.constructors.append(new_constructor)
                                    if self.debug:
                                        print(f"Built constructor, total: {len(self.constructors)}")
                    # Close menus on outside click
                    if (self.show_guide or self.show_build_menu) and not (
                        (620 <= event.pos[0] <= 700 and 460 <= event.pos[1] <= 570) or  # Buttons
                        (300 <= event.pos[0] <= 500 and 150 <= event.pos[1] <= 350) or  # Build menu
                        guide_active  # Guide (Start Game overlaps)
                    ):
                        self.show_guide = False
                        self.show_build_menu = False
                        if self.debug:
                            print(f"Closed menus at ({event.pos[0]}, {event.pos[1]})")
                    # Startup or game over screens
                    if not self.game_started and 350 <= event.pos[0] <= 450 and 500 <= event.pos[1] <= 540:
                        self.game_started = True
                        self.last_metal_tick = self.time.time()
                        self.last_combat_tick = self.time.time()
                        if self.debug:
                            print("Game started")
                    elif self.game_over and 350 <= event.pos[0] <= 450 and 500 <= event.pos[1] <= 540:
                        self.reset_game()
                        if self.debug:
                            print("Game restarted")
                    # Tile selection
                    elif event.pos[0] < 600 and event.pos[1] < 600:
                        selected_scout = None
                        for scout in self.scouts:
                            if scout.x == x and scout.y == y:
                                selected_scout = scout
                                break
                        if selected_scout:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                if selected_scout in self.selected:
                                    self.selected.remove(selected_scout)
                                else:
                                    self.selected.append(selected_scout)
                                if self.debug:
                                    print(f"Shift-toggled scout at ({x}, {y}), selected: {len(self.selected)}")
                            else:
                                self.selected = [selected_scout]
                                if self.debug:
                                    print(f"Selected scout at ({x}, {y})")
                        else:
                            for colony in self.colonies:
                                if colony.x == x and colony.y == y and not any(isinstance(sel, unit.Scout) for sel in self.selected):
                                    self.selected = [colony]
                                    if self.debug:
                                        print(f"Selected colony at ({x}, {y})")
                                    break
                            else:
                                self.selected = []
                                if self.debug:
                                    print(f"Deselected at ({x}, {y})")
                elif event.button == 3 and self.selected and all(isinstance(sel, unit.Scout) for sel in self.selected):
                    for scout in self.selected:
                        scout.move_to(x, y, self)
                    if self.debug:
                        print(f"Moved {len(self.selected)} scouts to ({x}, {y})")

    def __del__(self):
        pygame.quit()
