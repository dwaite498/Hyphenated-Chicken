from settings import MOVE_TICK_RATE, BUILD_TIME

class Scout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 5
        self.last_move = 0
        self.target_x = x
        self.target_y = y

    def move_to(self, x, y, game):
        current_time = game.time.time()
        if current_time - self.last_move < MOVE_TICK_RATE:
            return False
        # Check friendly unit collision and enemy ZOC (8 directions)
        friendly_positions = [(u.x, u.y) for u in game.scouts + game.constructors + game.colonies if u != self]
        enemy_positions = [(e.x, e.y) for e in game.enemies]
        adjacent_to_enemy = any(abs(self.x - ex) <= 1 and abs(self.y - ey) <= 1 for ex, ey in enemy_positions)
        if (x, y) in friendly_positions:
            return False
        if adjacent_to_enemy:
            dx, dy = x - self.x, y - self.y
            if dx == 0 and dy == 0:  # Stay still
                return True
            if not (dx > 0 and self.x < ex or dx < 0 and self.x > ex or dy > 0 and self.y < ey or dy < 0 and self.y > ey for ex, ey in enemy_positions):
                return False  # Can only move away
        for ex, ey in enemy_positions:
            if abs(x - ex) <= 1 and abs(y - ey) <= 1 and not adjacent_to_enemy:
                return False  # Can't move into ZOC
        # Set target for step-by-step movement
        self.target_x, self.target_y = x, y
        return True

    def update(self, game):
        current_time = game.time.time()
        if current_time - self.last_move >= MOVE_TICK_RATE and (self.x != self.target_x or self.y != self.target_y):
            friendly_positions = [(u.x, u.y) for u in game.scouts + game.constructors + game.colonies if u != self]
            enemy_positions = [(e.x, e.y) for e in game.enemies]
            adjacent_to_enemy = any(abs(self.x - ex) <= 1 and abs(self.y - ey) <= 1 for ex, ey in enemy_positions)
            next_x, next_y = self.x, self.y
            if self.x < self.target_x:
                next_x += 1
            elif self.x > self.target_x:
                next_x -= 1
            elif self.y < self.target_y:
                next_y += 1
            elif self.y > self.target_y:
                next_y -= 1
            if 0 <= next_x < game.planet["width"] and 0 <= next_y < game.planet["height"] and (next_x, next_y) not in friendly_positions:
                if adjacent_to_enemy:
                    dx, dy = next_x - self.x, next_y - self.y
                    if not any((dx > 0 and self.x < ex or dx < 0 and self.x > ex or dy > 0 and self.y < ey or dy < 0 and self.y > ey) for ex, ey in enemy_positions):
                        return
                for ex, ey in enemy_positions:
                    if abs(next_x - ex) <= 1 and abs(next_y - ey) <= 1 and not adjacent_to_enemy:
                        return
                self.x, self.y = next_x, next_y
                self.last_move = current_time
                self.reveal_tiles(game)

    def reveal_tiles(self, game):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x, y = self.x + dx, self.y + dy
                if 0 <= x < game.planet["width"] and 0 <= y < game.planet["height"]:
                    if [x, y] in game.planet["resources"]["metal"]:
                        game.fog[y][x] = "M"
                    elif [x, y] in game.planet["enemies"]:
                        game.fog[y][x] = "E"
                    else:
                        game.fog[y][x] = game.planet["tiles"][y][x]

class Constructor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 2
        self.building = False
        self.build_start_time = None

    def start_building(self, game):
        if not self.building and [self.x, self.y] in game.planet["resources"]["metal"]:
            self.building = True
            self.build_start_time = game.time.time()
            game.planet["resources"]["metal"].remove([self.x, self.y])  # Consume mineral

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 10
