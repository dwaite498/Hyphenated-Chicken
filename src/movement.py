from settings import MOVE_TICK_RATE

def update(game):
    current_time = game.time.time()
    if current_time - game.last_metal_tick >= MOVE_TICK_RATE:
        for scout in game.scouts:
            scout.update(game)
        game.last_metal_tick = current_time
