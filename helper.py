#a bit of a workaround



class helper():
	
	def __init__(self):
		self.players = []
		self.spawns = []
		
	def add_player(self, new_player):
		self.players.append(new_player)

	def get_player(self, ind):
		return self.players[ind]
		
	def add_spawn(self, new_spawn):
		self.spawns.append(new_spawn)