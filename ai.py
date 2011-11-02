import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class ai_node(object):
	def __init__(self, x, y, i):
		self.xpos = x
		self.ypos = y
		self.id = i
		self.loadModel()
		self.setupCollisions()

	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.setPos((self.xpos, self.ypos, self.zpos))
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('path-node-%fn')
		
		cSphere = CollisionSphere(0, 0, 0, 5)
		name_string = "ai-node-"#+str(self.id)
		cNode = CollisionNode(name_string)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
class node_handler(object):
	def __init__(self):
		self.path = []
		populate_nodes(self):
		
	def populate_nodes(self):
		f = open('/load_files/path_nodes.txt', 'r')
		#read in nodes from file
		for line in f:
			for words in split(line):
				self.path.append(ai_node(words[0], words[1], words[2]))
				
	def checkpoint(self):
		self.path.append(self.path.pop(0))
				
			
