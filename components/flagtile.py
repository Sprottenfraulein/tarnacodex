class FlagTile:
    def __init__(self, obj=None, door=None, mon=None, trap=None, item=None, light=False, mov=False, vis=False, map=False, floor=False):
        self.obj = obj
        self.door = door
        self.mon = mon
        self.trap = trap
        self.item = item
        self.light = light
        self.mov = mov
        self.vis = vis
        self.map = map
        self.floor = floor