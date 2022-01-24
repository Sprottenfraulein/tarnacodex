# Animations counter object


class Counter:
	def __init__(self, fps, spr, max_rounds):
		self.frame = 0
		self.step = 0
		self.rounds = 0
		self.fps = fps
		self.spr = spr
		self.max_rounds = max_rounds

	def tick(self):
		self.frame += 1
		if self.frame >= self.fps:
			self.frame = 0
			self.step += 1
			if self.step >= self.spr:
				self.step = 0
				self.rounds += 1
				if self.max_rounds is not None and self.rounds >= self.max_rounds:
					self.rounds = 0
		return self.step
