import json
import os
import time
import pygame
from colony import Colony
from settings import MAP_WIDTH, MAP_HEIGHT, TICK_RATE, WINDOW_SIZE, TILE_SIZE

class Game:
    def __init__(self):
        pygame.init()
        self.time = time  # Alias for testing
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Planet Colonization")
        self.clock = pygame.time.Clock()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        planet_path = os.path.join(script_dir, "..", "data", "planet.json")
        with open(planet_path, "r") as f:
            self.planet = json.load(f)
        self.colony = Colony(5, 5)  # Centered on 10x10
        self.fog = [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.fog[5][5] = 'C'
        self.scout = None
        self.running = True
        self.last_tick = self.time.time()
        self.font = pygame.font.SysFont(None, 24)

    def run(self):
        print("Game loop starting...")
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.scout:
                    self.scout = self.colony.build_scout()
                elif self.scout:
                    if event.key == pygame.K_UP:
                        self.scout.move("north", self)
                    elif event.key == pygame.K_DOWN:
                        self.scout.move("south", self)
                    elif event.key == pygame.K_LEFT:
                        self.scout.move("west", self)
                    elif event.key == pygame.K_RIGHT:
                        self.scout.move("east", self)

    def update(self):
        current_time = self.time.time()
        if current_time - self.last_tick >= TICK_RATE:
            self.colony.update()
            self.last_tick = current_time

    def render(self):
        self.screen.fill((0, 0, 0))  # Black background
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.fog[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == '?':
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)  # Gray fog
                elif tile == 'C':
                    pygame.draw.rect(self.screen, (0, 255, 0), rect)  # Green colony
                elif tile == 'S':
                    pygame.draw.rect(self.screen, (0, 0, 255), rect)  # Blue scout
                elif tile == 'M':
                    pygame.draw.rect(self.screen, (255, 255, 0), rect)  # Yellow metal
                elif tile == 'E':
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)  # Red enemy
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)  # Grid lines
        if self.scout and self.fog[self.scout.y][self.scout.x] != 'C':
            rect = pygame.Rect(self.scout.x * TILE_SIZE, self.scout.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, (0, 0, 255), rect)  # Scout overlay
        metal_text = self.font.render(f"Metal: {self.colony.metal}", True, (255, 255, 255))
        self.screen.blit(metal_text, (10, 10))
        pygame.display.flip()

    def __del__(self):
        pygame.quit()
