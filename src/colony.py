class Colony:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.metal = 0
        self.health = 20

    def update(self):
        from settings import METAL_TICK_RATE
        self.metal += METAL_TICK_RATE

    def build_scout(self):
        if self.metal >= 5:
            self.metal -= 5
            from unit import Scout
            return Scout(self.x, self.y)
        return None

    def build_constructor(self):
        if self.metal >= 25:
            self.metal -= 25
            from unit import Constructor
            return Constructor(self.x, self.y)
        return None

    def get_status(self):
        return f"Colony at ({self.x}, {self.y}) - Metal: {self.metal}, Health: {self.health}"
