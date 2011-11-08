#a bit of a workaround



class helper():
	glob_players = []
	
	def __init__(self):
		self.players = []
		
	def add_player(self, new_player):
		self.players.append(new_player)
		glob_players = self.players
		print(len(glob_players))

	def get_player(self, ind):
		return self.players[ind]