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
        self.scout = None
        self.selected = None
        self.running = True
        self.paused = False
        self.last_metal_tick = self.time.time()
        self.last_flash = self.time.time()
        self.flash_on = True
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
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                if event.button == 1:  # Left click
                    if self.fog[y][x] == 'C':
                        self.selected = self.colony
                    elif self.scout and self.fog[y][x] == 'S':
                        self.selected = self.scout
                    else:
                        self.selected = None
                elif event.button == 3 and self.scout and self.selected == self.scout:  # Right click
                    self.scout.move_to(x, y, self)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not self.scout:
                x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                if self.fog[y][x] == 'C':
                    self.scout = self.colony.build_scout()

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
                    if self.scout and self.scout.x == x and self.scout.y == y and self.flash_on:
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
                elif self.selected == self.scout and x == self.scout.x and y == self.scout.y:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        metal_text = self.font.render(f"Metal: {self.colony.metal}", True, (255, 255, 255))
        self.screen.blit(metal_text, (10, 10))
        hud_text = ""
        if self.selected == self.colony:
            hud_text = f"Colony at (5,5) - Metal: {self.colony.metal}"
        elif self.selected == self.scout:
            hud_text = f"Scout at ({self.scout.x}, {self.scout.y})"
        if hud_text:
            hud_render = self.font.render(hud_text, True, (255, 255, 255))
            self.screen.blit(hud_render, (10, 30))
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
        if self.paused:
            pause_text = self.font.render("Paused", True, (255, 255, 255))
            self.screen.blit(pause_text, (WINDOW_SIZE // 2 - 30, WINDOW_SIZE // 2))
        pygame.display.flip()

    def __del__(self):
        pygame.quit()
