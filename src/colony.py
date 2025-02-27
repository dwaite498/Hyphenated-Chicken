class Colony:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.metal = 0

    def update(self):
        from settings import METAL_RATE
        self.metal += METAL_RATE  # Real-time resource production

    def get_status(self):
        return f"Colony at ({self.x}, {self.y}) - Metal: {self.metal}"
