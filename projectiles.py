import sys, math, random
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions

class Projectile(object):
	def __init__(self, vel, x, y, z, angle, range, playerid, id):
		self.xvel = vel*math.sin(angle)
		self.yvel = vel*-math.cos(angle)
		self.zvel = 0
		self.origx = x
		self.origy = y
		self.trajectory = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.prevtime = 0
		self.range = range
		self.playerid = playerid
		self.id = id
		
		self.loadModel()
		self.setupCollisions()
		#if self.playerid != 0:
		#	self.accept("projectile:" + self.playerid + ":" + self.id + "-collide-player", self.kill)
		
		#for i in range(1:8):
		#	if i != int(self.playerid):
		#		self.accept("projectile:" + self.playerid + ":" + self.id + "-collide-ai" + str(i), self.kill)
			
	
	def loadModel(self):
		"""loads the bullet model"""
		#load the proxy model
		self.form = loader.loadModel("models/panda-model")
		self.form.setScale(.005)
		self.form.reparentTo(render)
	
	def setupCollisions(self):
		#run through the gambit
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		identifier = "projectile:" + str(self.playerid) + ":" + str(self.id)
		self.cHandler.setInPattern(identifier+"-collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode(identifier)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	#def update(self, task):
	def update(self, elapsed):
		"""moves the bullet in a straight line relative to its trajectory"""
		#elapsed = task.time - self.prevtime
		self.xpos = self.xpos + self.xvel*elapsed
		self.ypos = self.ypos + self.yvel*elapsed
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		
		#check to see if the projectile is out of range
		if math.sqrt((self.origx-self.xpos)**2 + (self.origy-self.ypos)**2) > self.range:
			 #kill the projectile
			 self.form.removeNode()
			 return False
		
		#self.prevtime = task.time
		#return Task.cont
		return True
			
	def kill(self, cEntry):
		"""destroys the bullet upon entering a foreign body"""
		#player_identifier = cEntry.getIntoNodePath().getName()
		cEntry.getFromNodePath().getParent().remove()
	
class Flames(DirectObject):
	def __init__(self, x, y, z, angle):
		self.xpos = x + 100
		self.ypos = y + 100
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = -1
		#may need to play around with this value
		self.duration = 100
		self.penalty = 1
		
	def loadModel(self):
		"""loads the flame model"""
		#will likely need to change this to an actor
		self.form = loader.loadModel("models/panda-model")
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		"""sets up the flamebox to burn things"""
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('burned-up-%in')
		
		cSphere = CollisionSphere((0,0,0),3) 
		cNode = CollisionNode("flames")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def update(self, elapsed):
	#def update(self, task):
		"""the fire sticks around for a second and then disappears"""
		#elapsed = 0
		#if self.prevtime == -1:	
		#	elapsed = 0
		#else:
		#	elapsed = task.time - self.prevtime
			
		self.duration -= elapsed
			
		if self.duration <= 0:
			self.form.removeNode()
			return False
		
		#	self.prevtime = task.time
		#	return Task.cont
		return True
	
class Bomb(DirectObject):
	def __init__(self, x, y, z, angle):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = -1
		self.countdown = 3.0
		self.exploderange = 10.0
		self.penalty = 100
		self.accept('bomb-detonated-player', self.explode)
	
	def loadModel(self):
		"""loads the bomb model"""
		self.form = loader.loadModel("models/panda-model")
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		"""sets the bomb up to collide with things"""
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('bomb-detonated-%in')
		
		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode("bomb")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def update(self, elapsed):
	#def update(self, task):
		"""the bomb sits until someone runs into it or its timer goes off"""
		#elapsed = 0
		#if self.prevtime == -1:
		#	elapsed = 0
		#else:
		#	elapsed = task.time - self.prevtime
		
		self.countdown = self.countdown - elapsed
		
		if self.countdown <= 0:
			self.explode()
			self.form.removeNode()
			return False
		
		#self.prevtime = task.time
		#return Task.cont
		return True
	
	#need to test to see if the explosion is lasting long enough to collide with anything
	#before being removed
	def explode(self):	
		"""the bomb explodes"""
		#base.cTrav = CollisionTraverser()
		self.cHandler2 = CollisionHandlerEvent()
		self.cHandler2.setInPattern('blew-up-%in')
		
		explosionSphere = CollisionSphere(self.xpos, self.ypos, self.zpos, self.exploderange)
		cNode = CollisionNode("explosion")
		cNode.addSolid(explosionSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler2)
		