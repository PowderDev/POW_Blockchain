from multiprocessing import Process


class MiningProcess(Process):
	def __init__(self, target, args):
		super().__init__(target=target, args=args)
		self.killed = False
	
	def start(self):
		self.killed = False
		super().start()
	
	def kill(self):
		self.killed = True
		super().kill()
