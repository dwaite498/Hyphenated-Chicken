class Player:
    def __init__(self):
        self.location = STARTING_ROOM
        self.inventory = []

    def move(self, new_location):
        self.location = new_location
        print(f"You move to the {new_location}.")

    def take(self, item):
        self.inventory.append(item)
        print(f"You take the {item}.")