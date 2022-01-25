# Item list


class ItemList(list):
    def __init__(self, filters=None, items_max=None):
        super().__init__()

        if filters is None:
            self.filters = dict()
        else:
            self.filters = filters

        self.items_max = items_max

