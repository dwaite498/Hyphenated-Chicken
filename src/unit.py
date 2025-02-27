from settings import MOVE_TICK_RATE, BUILD_TIME

class Scout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 5
        self.last_move = 0

    def move_to(self, x, y, game):
        current_time = game.time.time()
        if current_time - self.last_move < MOVE_TICK_RATE:
            return False
        if 0 <= x < game.planet["width"] and 0 <= y < game.planet["height"]:
            self.x, self.y = x, y
            self.last_move = current_time
            self.reveal_tiles(game)
            return True
        return False

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
