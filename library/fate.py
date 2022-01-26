from library import maths


class Fate:
    def __init__(self, range_low=1, range_high=1000, expolambda=0.004, chunk_size=100):
        self.range_low = range_low
        self.range_high = range_high
        self.expolambda = expolambda
        self.chunk_size = chunk_size
        self.expo_chunk = None

        self.chunk_reroll()

    def chunk_reroll(self):
        sample_list = [maths.expo_rnd_sample(self.range_low, self.range_high, self.expolambda) for i in range(0, self.chunk_size)]
        self.expo_chunk = list(filter(lambda x: x is not None, sample_list))

    def expo_rnd(self, rnd_min=None, rnd_max=None):
        if rnd_min is None:
            rnd_min = self.range_low
        if rnd_max is None:
            rnd_max = self.range_high

        if len(self.expo_chunk) == 0:
            self.chunk_reroll()

        expo_origin = self.expo_chunk.pop()

        spread = rnd_max - rnd_min
        result = expo_origin * spread // 1000 + rnd_min

        return result
