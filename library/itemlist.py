# Item list


class ItemList(list):
    def __init__(self, filters=None, items_max=None, all_to_none=False):
        super().__init__()

        if filters is None:
            self.filters = dict()
        else:
            self.filters = filters

        self.items_max = items_max

        if all_to_none and self.items_max is not None:
            for i in range(0, self.items_max):
                super().append(None)

