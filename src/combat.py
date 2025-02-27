from settings import COMBAT_TICK_RATE, BUILD_TIME
import unit

def update(game):
    current_time = game.time.time()
    if current_time - game.last_combat_tick >= COMBAT_TICK_RATE:
        # Combat logic (8 directions, no friendly fire)
        for colony in game.colonies[:]:
            targets = []
            for enemy in game.enemies:
                if abs(enemy.x - colony.x) <= 1 and abs(enemy.y - colony.y) <= 1:
                    targets.append(enemy)
            if targets:
                target = targets[0]
                target.health -= 1
                if target.health <= 0:
                    game.enemies.remove(target)
        for scout in game.scouts[:]:
            targets = []
            for enemy in game.enemies:
                if abs(enemy.x - scout.x) <= 1 and abs(enemy.y - scout.y) <= 1:
                    targets.append(enemy)
            if targets:
                target = targets[0]
                target.health -= 1
                if target.health <= 0:
                    game.enemies.remove(target)
        for enemy in game.enemies[:]:
            targets = []
            for scout in game.scouts:
                if abs(scout.x - enemy.x) <= 1 and abs(scout.y - enemy.y) <= 1:
                    targets.append(scout)
            for colony in game.colonies:
                if abs(colony.x - enemy.x) <= 1 and abs(colony.y - enemy.y) <= 1:
                    targets.append(colony)
            if targets:
                target = targets[0]
                target.health -= 1
                if target.health <= 0:
                    if isinstance(target, unit.Scout):
                        game.scouts.remove(target)
                        if target in game.selected:
                            game.selected.remove(target)
                    elif isinstance(target, Colony):
                        game.colonies.remove(target)
                        if target in game.selected:
                            game.selected.remove(target)
        # Constructor building
        for constructor in game.constructors[:]:
            if constructor.health <= 0:
                game.constructors.remove(constructor)
                if game.debug:
                    print(f"Constructor destroyed at ({constructor.x}, {constructor.y})")
            elif not constructor.building:
                constructor.start_building(game)
            elif current_time - constructor.build_start_time >= BUILD_TIME:
                game.colonies.append(Colony(constructor.x, constructor.y))
                game.constructors.remove(constructor)
                game.fog[constructor.y][constructor.x] = 'C'
                if game.debug:
                    print(f"New colony built at ({constructor.x}, {constructor.y})")
        game.last_combat_tick = current_time
        # Check game over
        if not game.colonies:
            game.game_over = True
            if game.debug:
                print("Game over - no colonies remaining")
