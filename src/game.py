import json
import os
import time
import pygame
from colony import Colony
from settings import MAP_WIDTH, MAP_HEIGHT, MOVE_TICK_RATE, METAL_TICK_RATE, WINDOW_SIZE, TILE_SIZE, FLASH_RATE

class Game:
    def __init__(self):
        pygame.init()
        self.time = time
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Planet Colonization")
        self.clock = pygame.time.Clock()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colony = Colony(5, 5)
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[5][5] = 'C'
        self.scouts = []  # List for multiple scouts
        self.selected = None
        self.running = True
        self.paused = False
        self.last_metal_tick = self.time.time()
        self.last_flash = self.time.time()
        self.flash_on = True
        self.show_guide = False
        self.show_build_menu = False
        self.debug = False
        self.font = pygame.font.SysFont(None, 24)

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                if event.button == 1:  # Left click
                    # Selection
                    selected_scout = None
                    for scout in self.scouts:
                        if scout.x == x and scout.y == y:
                            selected_scout = scout
                            break
                    if selected_scout:
                        self.selected = selected_scout
                        if self.debug:
                            print(f"Selected scout at ({x}, {y})")
                    elif self.fog[y][x] == 'C' and not selected_scout:
                        self.selected = self.colony
                        if self.debug:
                            print(f"Selected colony at ({x}, {y})")
                    else:
                        self.selected = None
                        if self.debug:
                            print(f"Deselected at ({x}, {y})")
                    # Guide button
                    if WINDOW_SIZE - 100 <= event.pos[0] <= WINDOW_SIZE - 20 and WINDOW_SIZE - 40 <= event.pos[1] <= WINDOW_SIZE - 10:
                        self.show_guide = not self.show_guide
                        self.show_build_menu = False
                        if self.debug:
                            print(f"Guide toggled: {self.show_guide}")
                    # Build button
                    elif WINDOW_SIZE - 190 <= event.pos[0] <= WINDOW_SIZE - 110 and WINDOW_SIZE - 40 <= event.pos[1] <= WINDOW_SIZE - 10:
                        if self.selected == self.colony:
                            self.show_build_menu = not self.show_build_menu
                            self.show_guide = False
                            if self.debug:
                                print(f"Build menu toggled: {self.show_build_menu}")
                    # Build menu scout button
                    elif self.show_build_menu and 250 <= event.pos[0] <= 350 and 300 <= event.pos[1] <= 340:
                        if self.colony.metal >= 5 and self.selected == self.colony:
                            new_scout = self.colony.build_scout()
                            if new_scout:
                                self.scouts.append(new_scout)
                                if self.debug:
                                    print(f"Built scout, total scouts: {len(self.scouts)}")
                    # Close menus on outside click
                    if (self.show_guide or self.show_build_menu) and not (
                        (150 <= event.pos[0] <= 450 and 200 <= event.pos[1] <= 400) or  # Guide
                        (250 <= event.pos[0] <= 450 and 250 <= event.pos[1] <= 350) or  # Build menu
                        (WINDOW_SIZE - 190 <= event.pos[0] <= WINDOW_SIZE - 20 and WINDOW_SIZE - 40 <= event.pos[1] <= WINDOW_SIZE - 10)  # Buttons
                    ):
                        self.show_guide = False
                        self.show_build_menu = False
                        if self.debug:
                            print(f"Closed menus at ({event.pos[0]}, {event.pos[1]})")
                elif event.button == 3 and self.selected in self.scouts:  # Right click
                    self.selected.move_to(x, y, self)
                    if self.debug:
                        print(f"Moved scout to ({x}, {y})")

    def update(self):
        current_time = self.time.time()
        if current_time - self.last_metal_tick >= METAL_TICK_RATE:
            self.colony.update()
            self.last_metal_tick = current_time
        if current_time - self.last_flash >= FLASH_RATE:
            self.flash_on = not self.flash_on
            self.last_flash = current_time

    def render(self):
        self.screen.fill((0, 0, 0))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_x, hover_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.fog[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == '?':
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
                elif tile == 'C':
                    pygame.draw.rect(self.screen, (0, 255, 0), rect)
                    for scout in self.scouts:
                        if scout.x == x and scout.y == y and self.flash_on:
                            pygame.draw.rect(self.screen, (0, 0, 255), rect)  # Flash scout
                elif tile == 'S':
                    pygame.draw.rect(self.screen, (0, 0, 255), rect)
                elif tile == 'M':
                    pygame.draw.rect(self.screen, (255, 255, 0), rect)
                elif tile == 'E':
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
                if self.selected == self.colony and x == 5 and y == 5:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                elif self.selected in self.scouts and x == self.selected.x and y == self.selected.y:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        # Metal display
        metal_text = self.font.render(f"Metal: {self.colony.metal}", True, (255, 255, 255))
        self.screen.blit(metal_text, (10, 10))
        # HUD for selection
        hud_text = ""
        if self.selected == self.colony:
            hud_text = f"Colony at (5,5) - Metal: {self.colony.metal}"
        elif self.selected in self.scouts:
            hud_text = f"Scout at ({self.selected.x}, {self.selected.y}) - Scouts: {len(self.scouts)}"
        if hud_text:
            hud_render = self.font.render(hud_text, True, (255, 255, 255))
            self.screen.blit(hud_render, (10, 30))
        # Hover info
        hover_text = ""
        if 0 <= hover_x < MAP_WIDTH and 0 <= hover_y < MAP_HEIGHT:
            tile = self.fog[hover_y][hover_x]
            if tile == 'C':
                hover_text = "Colony"
            elif tile == 'S':
                hover_text = "Scout"
            elif tile == 'M':
                hover_text = "Metal Deposit"
            elif tile == 'E':
                hover_text = "Enemy"
            elif tile == '?':
                hover_text = "Unexplored"
        if hover_text:
            hover_render = self.font.render(hover_text, True, (255, 255, 255))
            self.screen.blit(hover_render, (10, 580))
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(hover_x * TILE_SIZE, hover_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
        # Pause overlay
        if self.paused:
            pause_text = self.font.render("Paused", True, (255, 255, 255))
            self.screen.blit(pause_text, (WINDOW_SIZE // 2 - 30, WINDOW_SIZE // 2))
        # Guide button and pop-up
        guide_rect = pygame.Rect(WINDOW_SIZE - 100, WINDOW_SIZE - 40, 80, 30)
        pygame.draw.rect(self.screen, (150, 150, 150), guide_rect)
        guide_text = self.font.render("Guide", True, (0, 0, 0))
        self.screen.blit(guide_text, (WINDOW_SIZE - 80, WINDOW_SIZE - 35))
        if self.show_guide:
            guide_popup = pygame.Rect(WINDOW_SIZE // 2 - 150, WINDOW_SIZE // 2 - 100, 300, 200)
            pygame.draw.rect(self.screen, (255, 255, 255), guide_popup)
            pygame.draw.rect(self.screen, (0, 0, 0), guide_popup, 2)
            controls = [
                "Left Click: Select unit",
                "Right Click: Move selected scout",
                "Space: Pause/Unpause",
                "Build Button: Open build menu",
                "D: Toggle debug",
                "Hover: Show tile info"
            ]
            for i, line in enumerate(controls):
                text = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text, (WINDOW_SIZE // 2 - 140, WINDOW_SIZE // 2 - 90 + i * 30))
        # Build button and menu
        build_rect = pygame.Rect(WINDOW_SIZE - 190, WINDOW_SIZE - 40, 80, 30)
        pygame.draw.rect(self.screen, (150, 150, 150), build_rect)
        build_text = self.font.render("Build", True, (0, 0, 0))
        self.screen.blit(build_text, (WINDOW_SIZE - 170, WINDOW_SIZE - 35))
        if self.show_build_menu:
            build_menu = pygame.Rect(WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2 - 50, 200, 100)
            pygame.draw.rect(self.screen, (255, 255, 255), build_menu)
            pygame.draw.rect(self.screen, (0, 0, 0), build_menu, 2)
            scout_button = pygame.Rect(WINDOW_SIZE // 2 - 50, WINDOW_SIZE // 2 - 20, 100, 40)
            pygame.draw.rect(self.screen, (200, 200, 200), scout_button)
            scout_text = self.font.render("Scout (5 Metal)", True, (0, 0, 0))
            self.screen.blit(scout_text, (WINDOW_SIZE // 2 - 45, WINDOW_SIZE // 2 - 15))
        if self.debug:
            debug_text = f"Selected: {type(self.selected).__name__ if self.selected else 'None'}"
            debug_render = self.font.render(debug_text, True, (255, 255, 255))
            self.screen.blit(debug_render, (10, 50))
        pygame.display.flip()

    def __del__(self):
        pygame.quit()
