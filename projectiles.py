import sys, math, random
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions

class Projectile(object):
	def __init__(self, vel, x, y, z, angle, range):
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
			
	def kill(self, cEntry):
		"""destroys the bullet upon entering a foreign body"""
		cEntr.getIntoNodePath().getParent().remove()
	
		
#class Bullet(Projectile):
	
	