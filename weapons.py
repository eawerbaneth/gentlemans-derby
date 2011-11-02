import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import projectiles
import sys, math, random

#default weapon (revolver)
class Weapon(DirectObject):
	def __init__(self, x, y, z, angle, projectiles):
		self.keyMap = {"firing":0}
		self.prevtime = 0
		
		self.accept("space", self.setKey, ["firing", 1] )
		self.accept("space-up", self.setKey, ["firing", 0] )
		#note - projectiles should be an empty list the first time you create the weapon
		self.projectiles = projectiles
		
		#set weapon cooldown and how long it slows a player down for
		self.cooldown = 1.0
		self.penalty = 0.5
		self.ammo = 1000
		
		self.angle = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		
		self.LoadModel
	
	def LoadModel(self):
		self.form = Actor("models/weapons/revolverProxy.egg")
		self.form.reparentTo(render)
	
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
		
		if keyMap["firing"] and self.cooldown == 0 and self.ammo > 0:
			self.fire()
		
		for i, projectile in enumerate(self.projectiles):
			#update all projectiles belonging to this weapon,
			if not projectile.update(elapsed)
				#if the projectile was destroyed, get rid of it
				self.projectiles.pop(i)
	
		# if the player runs out of ammo (this will only happen on inherited classes, 
		# kill the thing and revert back to the pistol
		if self.ammo <= 0:
			self.kill()
			return false
		#note, when update returns false, you need to pass the weapon's projecitles
		#to the new pistol before destroying it
			
		return true
	
	def fire(self):
		"""pulls the trigger"""
		new_projectile = Projectile(5, self.xpos, self.ypos, self.zpos, self.angle, self.range, self.penalty)
		self.projectiles.append(new_projectile)
		self.cooldown = 1.0

	def kill(self):
		"""removes the weapon from the scene"""
		self.form.removeNode()
	
class GattlingGun(Weapon):
	def __init__(self, x, y, z, angle, projectiles):
		Weapon.__init__(self, x, y, z, angle, projectiles)
		self.coodown = 0.3
		self.penalty = 0.3
		self.ammo = 100

#using revolver proxy for now
	def LoadModel(self):
		self.form = Actor("models/weapons/revolverProxy.egg")
		self.form.reparentTo(render)
		
	def fire(self):
		"""pulls the trigger"""
		Weapon.fire(self)
		projectiles[projectiles.len()-1].penalty = 0.3
		self.cooldown = 0.3
		self.ammo = -= 1
	
class Flamethrower(Weapon):
	def __init__(self, x, y, z, angle, projectiles):
		Weapon.__init__(self, x, y, z, angle)
		self.ammo = 160
		self.cooldown = 0
		self.penalty = 0.1
	
#FLAG: waiting on image for this one
	def LoadModel(self):
		self.form = Actor("models/weapons/revolverProxy.egg")
		self.form.reparentTo(render)

	def fire(self):
	"""sprays fire"""
	#note: fire doesn't inherit from projectile class
	new_flames = Flames(self.xpos, self.ypos, self.zpos, self.angle)
	self.projectiles.append(new_flames)
	self.cooldown = 0
	self.ammo -= 1
		
	
class BombWeapon(Weapon):
	def __init__(self, x, y, z, angle, projectiles):
		Weapon.__init__(self, x, y, z, angle, projectiles)
		self.cooldown = 5.0
		self.penalty = 2.0
		self.ammo = 3
	
	#each individual method is going to need to load its own model
#FLAG: needs image
	def LoadModel(self):
		self.form = Actor("models/weapons/revolverProxy.egg")
		self.form.reparentTo(render)
	
	def fire(self):
		"""drops a bomb"""
		#note: bombs don't inherit from projectile class
		new_bomb = Bomb(self.xpos, self.ypos, self.zpos, self.angle)
		self.projectiles.append(new_bomb)
		self.cooldown = 5.0
		self.ammo -= 1
	
	