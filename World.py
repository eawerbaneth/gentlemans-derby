import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random
from weapons import *

class World(DirectObject):
	def __init__(self):
		base.disableMouse()
		camera.setPosHpr(0, -15, 7, 0, -15, 0)
		self.loadModels()
		self.collisionInit()
		
		self.keyMap = {"left":0, "right":0, "forward":0}
		taskMgr.add(self.move, "moveTask")
		self.prevtime = 0
		
		self.accept("escape", sys.exit)
		self.accept("arrow_up", self.setKey, ["forward", 1])
		self.accept("arrow_right", self.setKey, ["right", 1])
		self.accept("arrow_left", self.setKey, ["left", 1])
		self.accept("arrow_up-up", self.setKey, ["forward", 0])
		self.accept("arrow_right-up", self.setKey, ["right", 0])
		self.accept("arrow_left-up", self.setKey, ["left", 0])
		self.accept("collide-wall", self.putPlayer)
		
		#self.weapon = GattlingGun(0, 0, 20, 0, [])
		
		
	def setKey(self,key,value):
		self.keyMap[key] = value
		
	def putPlayer(self, cEntry):
		self.player.setPos(0,0,0)	
		
	def loadModels(self):
		self.player = Actor("models/panda-model")
		self.player.setScale(.005)
		self.player.setH(90)
		self.player.reparentTo(render)
		
		self.weapon = GattlingGun(0, 0, 100, 0, [])
		self.weapon.form.reparentTo(self.player)
		
		self.env = loader.loadModel("models/environment")
		self.env.reparentTo(render)
		self.env.setScale(.25)
		
	def move(self, task):
		elapsed = task.time - self.prevtime
		#camera.lookAt(self.player)
		if self.keyMap["left"]:
			self.player.setH(self.player.getH() + elapsed * 100)
		if self.keyMap["right"]:
			self.player.setH(self.player.getH() - elapsed * 100)
		if self.keyMap["forward"]:
			dist = 8 * elapsed
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		
		self.weapon.update(self.player.getX(), self.player.getY(), self.weapon.form.getZ(), deg2Rad(self.player.getH()), elapsed)
		self.prevtime = task.time
		return Task.cont
		
		
	def collisionInit(self):
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 500)
		cNode = CollisionNode("player")
		cNode.addSolid(cSphere)
		cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.player.attachNewNode(cNode)
		cNodePath.show()
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
		cSphere = CollisionInvSphere((0,0,0), 200)
		cNode = CollisionNode("wall")
		cNode.addSolid(cSphere)
		cNodePath = self.env.attachNewNode(cNode)
		cNodePath.show()
	
w = World()
run()	