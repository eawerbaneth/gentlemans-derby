import sys, math, random
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions

class Projectile(object):
	def __init__(self, vel, angle, x, y, z):
		self.xvel = vel*math.cos(angle)
		self.yvel = vel*math.sin(angle)
		self.zvel = 0
		self.trajectory = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.loadModel()
		self.setupCollisions()
	
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
		
		
class Bullet(Projectile):
	def loadModel()
	