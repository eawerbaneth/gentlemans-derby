import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class Boost(DirectObject):
	def __init__(self, x, y, z, angle):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = 0
		
	def loadModel(self):
		"""loads the boost model"""
#FLAG: still waiting on boost image
		self.form = loader.loadModel("models/panda-model")
		self.form.setScape(.005)
		self.form.reparentTo(render)	
			
	def setupCollisions(self):
		"""sets up the booster to detect collisions"""
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		#self.cHandler.setInPattern('%fn-sped-up')
		
		cQuad = CollisionPolygon(Point3(0, 0, 0), Point3(0, 0, 10), Point3(0, 10, 10), Point3(0, 10, 0))
		cNode = CollisionNode("speed_boost")
		cNode.addSolid(cQuad)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
class StreetLamp(DirectObject):
	def __init__(self, x, y, z):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.LoadModel()
		self.setupLights()
		
	def LoadModel(self):
		"""loads the lamp model"""
		self.form = loader.loadModel("models/lampExport")
		#self.form.setScale(.007)
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, -30)
		
	def setupLights(self):
		self.light = PointLight("streetlight")
		self.light.setColor((.2, .2, .2, .2))
		self.light.setPoint((self.xpos, self.ypos, self.zpos+3))
		self.nodepath = render.attachNewNode(self.light)
		#self.nodepath.setPos(self.xpos, self.ypos, self.zpos)
		render.setLight(self.nodepath)