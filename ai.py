import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class ai_node(object):
	def __init__(self, x, y, z, i):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.id = i
		self.loadModel()
		self.setupCollisions()
		
	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.setPos((self.xpos, self.ypos, self.zpos))
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		
		cSphere = CollisionSphere(x, y, z, 10)
		cNode = CollisionNode("ai-node-"+ str(i))
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)