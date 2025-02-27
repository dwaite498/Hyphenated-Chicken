from game import Game
import unit

if __name__ == "__main__":
    game = Game()
    game.unit = unit  # Alias for Enemy class access
    game.run()
