from settings import MOVE_TICK_RATE

class Scout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
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
