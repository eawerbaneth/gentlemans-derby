import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class bombSpawn(DirectObject):
	def __init__(self, x, y, z):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		
		self.prevtime = 0
		self.downtime = 0
		self.collectable = True
		
		self.loadModel()
		self.setupCollisions()
		self.cooldown = 20
		
		taskMgr.add(self.update, "bombSpawnUpdate")
		
	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		#self.form.setScale(3)
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		
		cSphere = CollisionSphere(0,0,0,4)
		cNode = CollisionNode("bombSpawn")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def kill(self):
		self.form.removeNode()
		
	def update(self, task):

		#print(self.collectable)
		elapsed = task.time - self.prevtime
		if(not self.collectable):
			self.downtime -= elapsed
		if(self.downtime < 0):
			self.downtime = 0
			self.collectable = True
			self.setupCollisions()
			
		self.prevtime = task.time
		return Task.cont
		
	def setDowntime(self):
		self.downtime = self.cooldown
		
class gatSpawn(DirectObject):
	def __init__(self, x, y, z):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		
		self.prevtime = 0
		self.downtime = 0
		self.collectable = True
		
		self.loadModel()
		self.setupCollisions()
		self.cooldown = 20
		
		taskMgr.add(self.update, "gatSpawnUpdate")
		
	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		#self.form.setScale(3)
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		
		cSphere = CollisionSphere(0,0,0,4)
		cNode = CollisionNode("gatSpawn")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def kill(self):
		self.form.removeNode()
		
	def update(self, task):

		#print(self.collectable)
		elapsed = task.time - self.prevtime
		if(not self.collectable):
			self.downtime -= elapsed
		if(self.downtime < 0):
			self.downtime = 0
			self.collectable = True
			self.setupCollisions()
			
		self.prevtime = task.time
		return Task.cont
		
	def setDowntime(self):
		self.downtime = self.cooldown