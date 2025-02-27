from settings import TICK_RATE

class Scout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_move = 0

    def move(self, direction, game):
        current_time = game.time.time()
        if current_time - self.last_move < TICK_RATE:
            return False
        new_x, new_y = self.x, self.y
        if direction == "north" and self.y > 0:
            new_y -= 1
        elif direction == "south" and self.y < game.planet["height"] - 1:
            new_y += 1
        elif direction == "west" and self.x > 0:
            new_x -= 1
        elif direction == "east" and self.x < game.planet["width"] - 1:
            new_x += 1
        else:
            return False
        self.x, self.y = new_x, new_y
        self.last_move = current_time
        self.reveal_tiles(game)
        return True

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
