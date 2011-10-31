import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

#default weapon (revolver)
class Weapon(DirectObject):
	def __init__(self, x, y, z, angle):
		self.keyMap = {"firing":0}
		self.prevtime = 0
		
		self.accept("space", self.setKey, ["firing", 1] )
		self.accept("space-up", self.setKey, ["firing", 0] )
		self.projectiles = []
		self.cooldown = 1.0
		
		self.angle = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		
		self.LoadModel
	
	def LoadModel(self):
		pass
	
	def setKey(self, key, value):
		self.keyMap[key] = value
	
	
	#note: angle is the angle that the player is facing
	#x, y, is the horizontal plane
	def update(self, x, y, z, angle, elapsed):
		"""you need to call update on the weapon every time you update player"""
		self.angle = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		
		self.cooldown = self.cooldown - elapsed
		if self.cooldown < 0.0
			self.cooldown = 0.0
		
		if keyMap["firing"] and self.cooldown == 0:
			self.fire()
		
		for i, projectile in enumerate(self.projectiles):
			#update all projectiles belonging to this weapon,
			if not projectile.update(elapsed)
				#if the projectile was destroyed, get rid of it
				self.projectiles.pop(i)
	
	
	def fire(self):
		"""pull the trigger"""
		new_projectile = projectile(5, x, y, z, angle, self.range)
		self.projectiles.append(new_projectile)
		self.cooldown = 1.0
		
	def kill(self):
		"""removes the weapon from the scene"""
		pass
	
		
class BombWeapon(Weapon):
	def __init__(self, x, y, z, angle):
		Weapon.__init__(self, x, y, z, angle)
		self.cooldown = 5.0
	
	#each individual method is going to need to load its own model
	def LoadModel(self):
		pass
	
	def fire(self):
		"""drops a bomb"""
		#note: bombs don't inherit from projectile class
		new_bomb = bomb(x, y, z, angle)
		self.projectiles.append(new_bomb)
		self.cooldown = 5.0
	

	
	
		
		
		