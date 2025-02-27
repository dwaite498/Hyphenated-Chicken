import json
import os
import time
import pygame
from colony import Colony
import unit
from settings import MAP_WIDTH, MAP_HEIGHT, MOVE_TICK_RATE, METAL_TICK_RATE, COMBAT_TICK_RATE, BUILD_TIME, WINDOW_SIZE, TILE_SIZE, FLASH_RATE

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
        self.last_flash = self.time.time()
        self.flash_on = True
        self.show_guide = False
        self.show_build_menu = False
        self.debug = False
        self.font = pygame.font.SysFont(None, 24)

    def reset_game(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colonies = [Colony(4, 4)]
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[4][4] = 'C'
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
        self.last_flash = self.time.time()
        self.flash_on = True
        self.show_guide = False
        self.show_build_menu = False

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_started and not self.paused and not self.game_over:
                self.update()
            self.render()
            self.clock.tick(60)

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
                elif event.key == pygame.K_b and self.colonies and self.colonies[0] in self.selected:
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
                        elif 500 <= event.pos[1] <= 530 and self.colonies and self.colonies[0] in self.selected:  # Build button
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
                    if self.show_build_menu and self.colonies and self.colonies[0] in self.selected:
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
                        elif self.fog[y][x] == 'C' and not any(isinstance(sel, unit.Scout) for sel in self.selected):
                            for colony in self.colonies:
                                if colony.x == x and colony.y == y:
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

    def update(self):
        current_time = self.time.time()
        if current_time - self.last_metal_tick >= METAL_TICK_RATE:
            for colony in self.colonies:
                colony.update()
            self.last_metal_tick = current_time
        if current_time - self.last_combat_tick >= COMBAT_TICK_RATE:
            # Combat logic
            for colony in self.colonies[:]:
                targets = []
                for scout in self.scouts:
                    if abs(scout.x - colony.x) + abs(scout.y - colony.y) == 1:
                        targets.append(scout)
                for enemy in self.enemies:
                    if abs(enemy.x - colony.x) + abs(enemy.y - colony.y) == 1:
                        targets.append(enemy)
                if targets:
                    target = targets[0]
                    target.health -= 1
                    if target.health <= 0:
                        if isinstance(target, unit.Scout):
                            self.scouts.remove(target)
                            if target in self.selected:
                                self.selected.remove(target)
                        else:
                            self.enemies.remove(target)
            for scout in self.scouts[:]:
                targets = []
                for enemy in self.enemies:
                    if abs(enemy.x - scout.x) + abs(enemy.y - scout.y) == 1:
                        targets.append(enemy)
                for colony in self.colonies:
                    if abs(colony.x - scout.x) + abs(colony.y - scout.y) == 1:
                        targets.append(colony)
                if targets:
                    target = targets[0]
                    target.health -= 1
                    if target.health <= 0 and isinstance(target, Colony):
                        self.colonies.remove(target)
                        if target in self.selected:
                            self.selected.remove(target)
            for enemy in self.enemies[:]:
                targets = []
                for scout in self.scouts:
                    if abs(scout.x - enemy.x) + abs(scout.y - enemy.y) == 1:
                        targets.append(scout)
                for colony in self.colonies:
                    if abs(colony.x - enemy.x) + abs(colony.y - enemy.y) == 1:
                        targets.append(colony)
                if targets:
                    target = targets[0]
                    target.health -= 1
                    if target.health <= 0:
                        if isinstance(target, unit.Scout):
                            self.scouts.remove(target)
                            if target in self.selected:
                                self.selected.remove(target)
                        elif isinstance(target, Colony):
                            self.colonies.remove(target)
                            if target in self.selected:
                                self.selected.remove(target)
            # Constructor building
            for constructor in self.constructors[:]:
                if constructor.health <= 0:
                    self.constructors.remove(constructor)
                    if self.debug:
                        print(f"Constructor destroyed at ({constructor.x}, {constructor.y})")
                elif not constructor.building:
                    constructor.start_building(self)
                elif current_time - constructor.build_start_time >= BUILD_TIME:
                    self.colonies.append(Colony(constructor.x, constructor.y))
                    self.constructors.remove(constructor)
                    self.fog[constructor.y][constructor.x] = 'C'
                    if self.debug:
                        print(f"New colony built at ({constructor.x}, {constructor.y})")
            # Scout movement
            for scout in self.scouts:
                scout.update(self)
            self.last_combat_tick = current_time
            # Check game over
            if not self.colonies:
                self.game_over = True
                if self.debug:
                    print("Game over - no colonies remaining")

    def render(self):
        self.screen.fill((0, 0, 0))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_x, hover_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
        if not self.game_started:
            self.screen.fill((100, 100, 100))
            title = self.font.render("Planet Colonization", True, (255, 255, 255))
            self.screen.blit(title, (WINDOW_SIZE[0] // 2 - 90, 50))
            controls = [
                "Left Click: Select unit",
                "Shift + Left: Multi-select scouts",
                "Right Click: Move selected scouts",
                "Space: Pause/Unpause",
                "B: Open build menu",
                "D: Toggle debug",
                "Hover: Show tile info"
            ]
            for i, line in enumerate(controls):
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (50, 100 + i * 30))
            start_rect = pygame.Rect(350, 500, 100, 40)
            pygame.draw.rect(self.screen, (150, 150, 150), start_rect)
            start_text = self.font.render("Start Game", True, (0, 0, 0))
            self.screen.blit(start_text, (360, 510))
        elif self.game_over:
            self.screen.fill((100, 100, 100))
            game_over_text = self.font.render("Game Over", True, (255, 0, 0))
            self.screen.blit(game_over_text, (WINDOW_SIZE[0] // 2 - 50, WINDOW_SIZE[1] // 2 - 20))
            restart_rect = pygame.Rect(350, 500, 100, 40)
            pygame.draw.rect(self.screen, (150, 150, 150), restart_rect)
            restart_text = self.font.render("Restart", True, (0, 0, 0))
            self.screen.blit(restart_text, (360, 510))
        else:
            # Game board
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    tile = self.fog[y][x]
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if tile == '?':
                        pygame.draw.rect(self.screen, (100, 100, 100), rect)
                    elif tile == 'C':
                        pygame.draw.rect(self.screen, (0, 255, 0), rect)
                    elif tile == 'M':
                        pygame.draw.rect(self.screen, (255, 255, 0), rect)
                    elif tile == 'E':
                        pygame.draw.rect(self.screen, (255, 0, 0), rect)
                    pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
            # Render units and colonies explicitly
            for colony in self.colonies:
                rect = pygame.Rect(colony.x * TILE_SIZE, colony.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (0, 255, 0), rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
                if colony in self.selected:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            for scout in self.scouts:
                rect = pygame.Rect(scout.x * TILE_SIZE, scout.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (0, 0, 255), rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
                if scout in self.selected:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                if scout.x != scout.target_x or scout.y != scout.target_y:
                    pygame.draw.line(self.screen, (255, 255, 255),
                                    (scout.x * TILE_SIZE + TILE_SIZE // 2, scout.y * TILE_SIZE + TILE_SIZE // 2),
                                    (scout.target_x * TILE_SIZE + TILE_SIZE // 2, scout.target_y * TILE_SIZE + TILE_SIZE // 2), 2)
            for constructor in self.constructors:
                rect = pygame.Rect(constructor.x * TILE_SIZE, constructor.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (255, 0, 255) if not constructor.building else (0, 255, 0) if self.flash_on else (255, 0, 255)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
            for enemy in self.enemies:
                if self.fog[enemy.y][enemy.x] != '?':
                    rect = pygame.Rect(enemy.x * TILE_SIZE, enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)
                    pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
            # Sidebar
            pygame.draw.rect(self.screen, (50, 50, 50), (600, 0, 200, 600))
            metal_text = self.font.render(f"Metal: {self.colonies[0].metal if self.colonies else 0}", True, (255, 255, 255))
            self.screen.blit(metal_text, (610, 10))
            hud_text = ""
            if self.selected and len(self.selected) == 1:
                sel = self.selected[0]
                if sel in self.scouts:
                    hud_text = f"Scout at ({sel.x}, {sel.y}) - HP: {sel.health}"
                elif sel in self.constructors:
                    if sel.building:
                        remaining = BUILD_TIME - int(self.time.time() - sel.build_start_time)
                        hud_text = f"Building at ({sel.x}, {sel.y}) - HP: {sel.health}, {remaining}s"
                    else:
                        hud_text = f"Constructor at ({sel.x}, {sel.y}) - HP: {sel.health}"
                elif sel in self.colonies:
                    hud_text = f"Colony at ({sel.x}, {sel.y}) - HP: {sel.health}"
            elif self.selected:
                hud_text = f"Selected: {len(self.selected)} Scouts"
            if hud_text:
                hud_render = self.font.render(hud_text, True, (255, 255, 255))
                self.screen.blit(hud_render, (610, 30))
            guide_rect = pygame.Rect(620, 540, 80, 30)
            pygame.draw.rect(self.screen, (150, 150, 150), guide_rect)
            guide_text = self.font.render("Guide", True, (0, 0, 0))
            self.screen.blit(guide_text, (640, 545))
            build_rect = pygame.Rect(620, 500, 80, 30)
            pygame.draw.rect(self.screen, (150, 150, 150), build_rect)
            build_text = self.font.render("Build", True, (0, 0, 0))
            self.screen.blit(build_text, (640, 505))
            restart_rect = pygame.Rect(620, 460, 80, 30)
            pygame.draw.rect(self.screen, (150, 150, 150), restart_rect)
            restart_text = self.font.render("Restart", True, (0, 0, 0))
            self.screen.blit(restart_text, (635, 465))
            # Hover info (board only)
            if 0 <= mouse_x < 600 and 0 <= mouse_y < 600:
                tile = self.fog[hover_y][hover_x]
                hover_text = ""
                if tile == 'C':
                    hover_text = "Colony"
                elif tile == 'S':
                    hover_text = "Scout"
                elif tile == 'M':
                    hover_text = "Metal Deposit"
                elif tile == 'E':
                    for enemy in self.enemies:
                        if enemy.x == hover_x and enemy.y == hover_y:
                            hover_text = f"Enemy - HP: {enemy.health}"
                            break
                elif tile == '?':
                    hover_text = "Unexplored"
                if hover_text:
                    hover_render = self.font.render(hover_text, True, (255, 255, 255))
                    self.screen.blit(hover_render, (10, 580))
                    pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(hover_x * TILE_SIZE, hover_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
            # Build menu
            if self.show_build_menu:
                build_menu = pygame.Rect(600, 150, 200, 200)
                pygame.draw.rect(self.screen, (255, 255, 255), build_menu)
                pygame.draw.rect(self.screen, (0, 0, 0), build_menu, 2)
                scout_button = pygame.Rect(610, 200, 100, 30)
                pygame.draw.rect(self.screen, (200, 200, 200), scout_button)
                scout_text = self.font.render("Scout (5)", True, (0, 0, 0))
                self.screen.blit(scout_text, (620, 205))
                constructor_button = pygame.Rect(610, 240, 100, 30)
                pygame.draw.rect(self.screen, (200, 200, 200), constructor_button)
                constructor_text = self.font.render("Constructor (25)", True, (0, 0, 0))
                self.screen.blit(constructor_text, (620, 245))
            # Pause overlay
            if self.paused:
                pause_text = self.font.render("Paused", True, (255, 255, 255))
                self.screen.blit(pause_text, (300, 300))
            # Debug
            if self.debug:
                debug_text = f"Selected: {len(self.selected)}, Scouts: {len(self.scouts)}, Constructors: {len(self.constructors)}"
                debug_render = self.font.render(debug_text, True, (255, 255, 255))
                self.screen.blit(debug_render, (10, 50))
        pygame.display.flip()

    def __del__(self):
        pygame.quit()
