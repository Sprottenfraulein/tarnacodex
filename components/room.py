class Room:
    def __init__(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.rating = 100
        self.adj_rooms = []
        self.doors = []
        self.traps = []
        self.corridor = False
        self.locked = False

    def inside(self, x, y):
        if self.left < x < self.right and self.top < y < self.bottom:
            return True
        else:
            return False