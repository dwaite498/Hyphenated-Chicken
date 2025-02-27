import pygame
from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, WINDOW_SIZE, FLASH_RATE

def render(game):
    game.screen.fill((0, 0, 0))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hover_x, hover_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
    font = pygame.font.SysFont(None, 24)
    if not game.game_started:
        game.screen.fill((100, 100, 100))
        title = font.render("Planet Colonization", True, (255, 255, 255))
        game.screen.blit(title, (WINDOW_SIZE[0] // 2 - 90, 50))
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
            text = font.render(line, True, (255, 255, 255))
            game.screen.blit(text, (50, 100 + i * 30))
        start_rect = pygame.Rect(350, 500, 100, 40)
        pygame.draw.rect(game.screen, (150, 150, 150), start_rect)
        start_text = font.render("Start Game", True, (0, 0, 0))
        game.screen.blit(start_text, (360, 510))
    elif game.game_over:
        game.screen.fill((100, 100, 100))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        game.screen.blit(game_over_text, (WINDOW_SIZE[0] // 2 - 50, WINDOW_SIZE[1] // 2 - 20))
        restart_rect = pygame.Rect(350, 500, 100, 40)
        pygame.draw.rect(game.screen, (150, 150, 150), restart_rect)
        restart_text = font.render("Restart", True, (0, 0, 0))
        game.screen.blit(restart_text, (360, 510))
    else:
        # Game board
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = game.fog[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == '?':
                    pygame.draw.rect(game.screen, (100, 100, 100), rect)
                elif tile == 'M':
                    pygame.draw.rect(game.screen, (255, 255, 0), rect)
                pygame.draw.rect(game.screen, (50, 50, 50), rect, 1)
        # Render units and colonies explicitly
        for colony in game.colonies:
            rect = pygame.Rect(colony.x * TILE_SIZE, colony.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(game.screen, (0, 255, 0), rect)
            pygame.draw.rect(game.screen, (50, 50, 50), rect, 1)
            if colony in game.selected:
                pygame.draw.rect(game.screen, (255, 255, 255), rect, 2)
        for scout in game.scouts:
            rect = pygame.Rect(scout.x * TILE_SIZE, scout.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(game.screen, (0, 0, 255), rect)
            pygame.draw.rect(game.screen, (50, 50, 50), rect, 1)
            if scout in game.selected:
                pygame.draw.rect(game.screen, (255, 255, 255), rect, 2)
            if scout.x != scout.target_x or scout.y != scout.target_y:
                mid_x = scout.x if scout.x == scout.target_x else scout.x + (scout.target_x - scout.x) / abs(scout.target_x - scout.x)
                mid_y = scout.y if scout.y == scout.target_y else scout.y + (scout.target_y - scout.y) / abs(scout.target_y - scout.y)
                pygame.draw.line(game.screen, (255, 255, 255),
                                (scout.x * TILE_SIZE + TILE_SIZE // 2, scout.y * TILE_SIZE + TILE_SIZE // 2),
                                (mid_x * TILE_SIZE + TILE_SIZE // 2, mid_y * TILE_SIZE + TILE_SIZE // 2), 2)
                pygame.draw.line(game.screen, (255, 255, 255),
                                (mid_x * TILE_SIZE + TILE_SIZE // 2, mid_y * TILE_SIZE + TILE_SIZE // 2),
                                (scout.target_x * TILE_SIZE + TILE_SIZE // 2, scout.target_y * TILE_SIZE + TILE_SIZE // 2), 2)
        for constructor in game.constructors:
            rect = pygame.Rect(constructor.x * TILE_SIZE, constructor.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = (255, 0, 255) if not constructor.building else (0, 255, 0) if game.flash_on else (255, 0, 255)
            pygame.draw.rect(game.screen, color, rect)
            pygame.draw.rect(game.screen, (50, 50, 50), rect, 1)
        for enemy in game.enemies:
            if game.fog[enemy.y][enemy.x] != '?':
                rect = pygame.Rect(enemy.x * TILE_SIZE, enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(game.screen, (255, 0, 0), rect)
                pygame.draw.rect(game.screen, (50, 50, 50), rect, 1)
        # Sidebar
        pygame.draw.rect(game.screen, (50, 50, 50), (600, 0, 200, 600))
        metal_text = font.render(f"Metal: {game.colonies[0].metal if game.colonies else 0}", True, (255, 255, 255))
        game.screen.blit(metal_text, (610, 10))
        hud_text = ""
        if game.selected and len(game.selected) == 1:
            sel = game.selected[0]
            if sel in game.scouts:
                hud_text = f"Scout at ({sel.x}, {sel.y}) - HP: {sel.health}"
            elif sel in game.constructors:
                if sel.building:
                    remaining = BUILD_TIME - int(game.time.time() - sel.build_start_time)
                    hud_text = f"Building at ({sel.x}, {sel.y}) - HP: {sel.health}, {remaining}s"
                else:
                    hud_text = f"Constructor at ({sel.x}, {sel.y}) - HP: {sel.health}"
            elif sel in game.colonies:
                hud_text = f"Colony at ({sel.x}, {sel.y}) - HP: {sel.health}"
        elif game.selected:
            hud_text = f"Selected: {len(game.selected)} Scouts"
        if hud_text:
            hud_render = font.render(hud_text, True, (255, 255, 255))
            game.screen.blit(hud_render, (610, 30))
        guide_rect = pygame.Rect(620, 540, 80, 30)
        pygame.draw.rect(game.screen, (150, 150, 150), guide_rect)
        guide_text = font.render("Guide", True, (0, 0, 0))
        game.screen.blit(guide_text, (640, 545))
        build_rect = pygame.Rect(620, 500, 80, 30)
        pygame.draw.rect(game.screen, (150, 150, 150), build_rect)
        build_text = font.render("Build", True, (0, 0, 0))
        game.screen.blit(build_text, (640, 505))
        restart_rect = pygame.Rect(620, 460, 80, 30)
        pygame.draw.rect(game.screen, (150, 150, 150), restart_rect)
        restart_text = font.render("Restart", True, (0, 0, 0))
        game.screen.blit(restart_text, (635, 465))
        # Hover info (board only)
        if 0 <= mouse_x < 600 and 0 <= mouse_y < 600:
            tile = game.fog[hover_y][hover_x]
            hover_text = ""
            if tile == 'C':
                for colony in game.colonies:
                    if colony.x == hover_x and colony.y == hover_y:
                        hover_text = f"Colony - HP: {colony.health}"
                        break
            elif tile == 'S':
                for scout in game.scouts:
                    if scout.x == hover_x and scout.y == hover_y:
                        hover_text = f"Scout - HP: {scout.health}"
                        break
            elif tile == 'M':
                hover_text = "Metal Deposit"
            elif tile == 'E':
                for enemy in game.enemies:
                    if enemy.x == hover_x and enemy.y == hover_y:
                        hover_text = f"Enemy - HP: {enemy.health}"
                        break
            elif tile == '?':
                hover_text = "Unexplored"
            if hover_text:
                hover_render = font.render(hover_text, True, (255, 255, 255))
                game.screen.blit(hover_render, (10, 580))
                pygame.draw.rect(game.screen, (255, 255, 255), pygame.Rect(hover_x * TILE_SIZE, hover_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
        # Guide pop-up
        if game.show_guide:
            guide_popup = pygame.Rect(300, 150, 200, 200)
            pygame.draw.rect(game.screen, (255, 255, 255), guide_popup)
            pygame.draw.rect(game.screen, (0, 0, 0), guide_popup, 2)
            controls = [
                "Left Click: Select",
                "Shift + Left: Multi-select",
                "Right Click: Move",
                "Space: Pause",
                "B: Build menu",
                "D: Debug"
            ]
            for i, line in enumerate(controls):
                text = font.render(line, True, (0, 0, 0))
                game.screen.blit(text, (310, 160 + i * 30))
        # Build menu
        if game.show_build_menu:
            build_menu = pygame.Rect(600, 150, 200, 200)
            pygame.draw.rect(game.screen, (255, 255, 255), build_menu)
            pygame.draw.rect(game.screen, (0, 0, 0), build_menu, 2)
            scout_button = pygame.Rect(610, 200, 100, 30)
            pygame.draw.rect(game.screen, (200, 200, 200), scout_button)
            scout_text = font.render("Scout (5)", True, (0, 0, 0))
            game.screen.blit(scout_text, (620, 205))
            constructor_button = pygame.Rect(610, 240, 100, 30)
            pygame.draw.rect(game.screen, (200, 200, 200), constructor_button)
            constructor_text = font.render("Constructor (25)", True, (0, 0, 0))
            game.screen.blit(constructor_text, (620, 245))
        # Pause overlay
        if game.paused:
            pause_text = font.render("Paused", True, (255, 255, 255))
            game.screen.blit(pause_text, (300, 300))
        # Debug
        if game.debug:
            debug_text = f"Selected: {len(game.selected)}, Scouts: {len(game.scouts)}, Constructors: {len(game.constructors)}"
            debug_render = font.render(debug_text, True, (255, 255, 255))
            game.screen.blit(debug_render, (10, 50))
