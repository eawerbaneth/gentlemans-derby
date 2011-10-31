import sys, math, random
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions

class Projectile(object):
	def __init__(self, vel, x, y, z, angle, range, penalty):
		self.xvel = vel*math.cos(angle)
		self.yvel = vel*math.sin(angle)
		self.zvel = 0
		self.origx = x
		self.origy = y
		self.trajectory = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.loadModel()
		self.setupCollisions()
		self.prevtime = 0
		self.range = range
		self.penalty = penalty
	
	def loadModel(self):
		"""loads the bullet model"""
		#load the proxy model
		self.form = loader.loadModel("proxy")
		self.form.reparentTo(render)
	
	def setupCollisions(self):
		#run through the gambit
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("shot-%in")
		
		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode("projectile")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	
	def update(self, task):
		"""moves the bullet in a straight line relative to its trajectory"""
		elapsed = task.time - self.prevtime
		self.xpos = self.xpos + self.xvel*math.cos(self.trajectory)*elapsed
		self.ypos = self.ypos + self.yvel*math.sin(self.trajectory)*elapsed
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		
		#check to see if the projectile is out of range
		if math.sqrt((self.origx-self.xpos)^2 + (self.origy-self.ypos)^2) > self.range:
			 #kill the projectile
			 self.form.removeNode()
		
		self.prevtime = task.time
		return Task.cont
			
	def kill(self, cEntry):
		"""destroys the bullet upon entering a foreign body"""
		cEntry.getIntoNodePath().getParent().remove()
	
class Bomb(DirectObject):
	def __init__(self, x, y, z, angle, penalty):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = -1
		self.countdown = 3.0
		self.exploderange = 10.0
		self.penalty = penalty
		self.accept('bomb-detonated-player', self.explode)
	
	def loadModel(self):
		"""loads the bomb model"""
		self.form = loader.loadModel("bombproxy")
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		"""sets the bomb up to collide with things"""
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('bomb-detonated-%in')
		
		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode("bomb")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def update(self, task):
		"""the bomb sits until someone runs into it or its timer goes off"""
		if self.prevtime == -1:
			elapsed = 0
		else:
			elapsed = task.time - self.prevtime
		
		self.countdown = self.countdown - elapsed
		
		if self.countdown <= 0:
			self.explode()
			self.form.removeNode()
		
		self.prevtime = task.time
		return Task.cont
	
	def explode(self):	
		"""the bomb explodes"""
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler('blew-up-%in')
		
		explosionSphere = CollisionSphere(self.xpos, self.ypos, self.zpos, self.exploderange)
		cNode = CollisionNode("explosion")
		Cnode.addSolid(explosionSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	
#class Bullet(Projectile):
	
	