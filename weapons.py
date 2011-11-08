import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
from projectiles import *
from helper import *
import sys, math, random

players = helper()



#default weapon (revolver)
class Weapon(DirectObject):
	def __init__(self, x, y, z, angle, bullets, id, projZ):
		self.keyMap = {"firing":0}
		self.prevtime = 0
		#id will be 0 for player, 1 - whatever for ai's
		self.playerid = id
		
		#print(players.players[1])
		
		if str(self.playerid) == "0":
			self.accept("space", self.setKey, ["firing", 1] )
			self.accept("space-up", self.setKey, ["firing", 0] )
		#note - projectiles should be an empty list the first time you create the weapon
		self.bullets = bullets
		
		#set weapon cooldown and how long it slows a player down for
		self.cooldown = 1.0
		self.penalty = 0.5
		self.ammo = 1000
		self.range = 30
		self.idLim = 1000
		self.projId = 0
		
		self.angle = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.projZ = projZ

		#for debugging purposes only
		#taskMgr.add(self.testing, "TESTING_WEAPON")
		self.prevtime = 0
		
		self.LoadModel()
		
	#DEBUGGING PURPOSES ONLY
	#def testing(self, task):
		#camera.lookAt(self.form)
	#	self.update(0, 0, 3, 0, task.time - self.prevtime)

		
	#	self.prevtime = task.time
		
	#	return Task.cont
		
	def LoadModel(self):


		self.form = Actor("models/weapons/revolverProxy")
		self.form.setScale(300)


		#self.form = loader.loadModel("models/weapons/revolverProxy")
		#self.form.setScale(.9)

		self.form.setPos(self.xpos,self.ypos,self.zpos)
		self.form.setH(90)
		#self.form.reparentTo(render)
	
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
		if self.cooldown < 0.0:
			self.cooldown = 0.0
		
		if self.keyMap["firing"] and self.cooldown == 0 and self.ammo > 0:
			self.fire()
		
		for i, projectile in enumerate(self.bullets):
			#update all projectiles belonging to this weapon,
			if not projectile.update(elapsed):
				#if the projectile was destroyed, get rid of it
				self.bullets.pop(i)
	
		# if the player runs out of ammo (this will only happen on inherited classes, 
		# kill the thing and revert back to the pistol
		if self.ammo <= 0:
			self.kill()
			return False
		#note, when update returns false, you need to pass the weapon's projecitles
		#to the new pistol before destroying it
			
		return True
	
	def fire(self):
		"""pulls the trigger"""

		#print(len(players.players))
		if(self.projId >= self.idLim):
			self.projId = 0
		new_projectile = Projectile(100, self.xpos, self.ypos, self.projZ, self.angle, 100, self.playerid, self.projId, len(self.bullets), players)
		self.bullets.append(new_projectile)
		self.projId = self.projId + 1
		
		#if self.playerid != 0:
		#	self.accept("projectile:" + str(self.playerid) + ":" + str(len(self.bullets)-1) + "-collision-player", self.address_bullet)
		#for i in range(1, 4):
		#	if str(i) != self.playerid:
		#		self.accept("projectile:" + str(self.playerid) + ":" + str(len(self.bullets)-1) + "-collision-ai"+str(i), self.address_bullet)
			
		self.cooldown = 1.0

	#occurs when there is a bullet collision
	def address_bullet(self, cEntry):
		"""called when a projectile collides with a player or ai"""
		print "bullet collision detected"
		#have the injured party incur a penalty
		handle = cEntry.getIntoNodePath().getName() #will be either ai<num> or player
		if handle == "player":
			players[0].take_damage(1)
		else:
			players[int(handle[2])].take_damage(1)
		
		#remove the bullet object
		cEntry.getFromNodePath().getParent().remove()
		
		
	def kill(self):
		"""removes the weapon from the scene"""
		self.form.cleanup()
		self.form.removeNode()
	
class GattlingGun(Weapon):
	def __init__(self, x, y, z, angle, bullets, id, projZ):
		Weapon.__init__(self, x, y, z, angle, bullets, id, projZ)
		self.coodown = 0.3
		self.penalty = 0.3
		self.ammo = 100

#using revolver proxy for now
	def LoadModel(self):
		self.form = Actor("models/gattlingExport")
		#self.form.setScale(300)
		self.form.setPos(self.xpos,self.ypos,self.zpos)
		self.form.setH(90)
		#self.form.reparentTo(render)
		
	def fire(self):
		"""pulls the trigger"""
		Weapon.fire(self)
		#self.bullets[len(self.bullets)-1].penalty = 0.3
		self.cooldown = 0.3
		self.ammo -= 1
	
class Flamethrower(Weapon):
	def __init__(self, x, y, z, angle, bullets, id, projZ):
		Weapon.__init__(self, x, y, z, angle, bullets, id, projZ)
		self.ammo = 160
		self.cooldown = 0
		self.penalty = 0.1
		self.range = 10
	
#FLAG: waiting on image for this one
	def LoadModel(self):
		self.form = Actor("models/weapons/revolverProxy")

		#self.form.reparentTo(render)

	def fire(self):
		"""sprays fire"""
		#note: fire doesn't inherit from projectile class
		new_flames = Flames(self.xpos, self.ypos, self.zpos, self.angle)
		self.bullets.append(new_flames)
		self.cooldown = 0
		self.ammo -= 1
		
	
class BombWeapon(Weapon):
	def __init__(self, x, y, z, angle, bullets, id, projZ):
		Weapon.__init__(self, x, y, z, angle, bullets, id, projZ)
		self.cooldown = 5.0
		self.penalty = 2.0
		self.ammo = 3
		self.range = 25
	
	#each individual method is going to need to load its own model
#FLAG: needs image
	def LoadModel(self):

		self.form = Actor("models/weapons/revolverProxy")

		#self.form.reparentTo(render)
	
	def fire(self):
		"""drops a bomb"""
		#note: bombs don't inherit from projectile class
		new_bomb = Bomb(self.xpos, self.ypos, self.zpos, self.angle)
		self.bullets.append(new_bomb)
		self.cooldown = 5.0
		self.ammo -= 1
	
	