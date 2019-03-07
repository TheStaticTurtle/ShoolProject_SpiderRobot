
class Smoother(object):
	"""docstring for Smoother"""
	def __init__(self,callback):
		super(Smoother, self).__init__()
		self.callback = callback
		self.current_angle = 90
		self.goto_angle = 90

	def goto(self,angle):
		self.goto_angle = angle

	def tick(self):
		if self.current_angle != self.goto_angle:
			diffrence = self.current_angle - self.goto_angle
			if diffrence < 0:
				self.callback(self.current_angle+1)
				self.current_angle = self.current_angle+1
			else:
				self.callback(self.current_angle-1)
				self.current_angle = self.current_angle-1

		