import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random
from weapons import *
from misc import *
from obstacles import *

class World(DirectObject):
	def __init__(self):
		base.disableMouse()
		camera.setPosHpr(0, -15, 7, 0, -15, 0)
		self.loadModels()
		self.setupLights()
		self.collisionInit()
		
		self.keyMap = {"left":0, "right":0, "forward":0, "down":0}
		taskMgr.add(self.move, "moveTask")
		self.prevtime = 0
		self.velocity = 0
		
		self.accept("escape", sys.exit)
		self.accept("arrow_up", self.setKey, ["forward", 1])
		self.accept("arrow_right", self.setKey, ["right", 1])
		self.accept("arrow_left", self.setKey, ["left", 1])
		self.accept("arrow_down", self.setKey, ["down", 1])
		self.accept("arrow_up-up", self.setKey, ["forward", 0])
		self.accept("arrow_right-up", self.setKey, ["right", 0])
		self.accept("arrow_left-up", self.setKey, ["left", 0])
		self.accept("arrow_down-up", self.setKey, ["down", 0])
		self.accept("collide-wall", self.putPlayer)
		
		self.weapon = GattlingGun(0, 0, 2, 0, [])
		self.lighttest = StreetLamp(self.player.getX(), self.player.getY(), self.player.getZ())
		self.spikestest = Spikes(3, 3, 3)
		
	def setKey(self,key,value):
		self.keyMap[key] = value
		
	def putPlayer(self, cEntry):
		self.player.setPos(0,0,0)	
		
	def loadModels(self):
		self.player = Actor("models/panda-model")
		self.player.setScale(.005)
		#self.player = Actor("models/weapons/revolverProxy")
		#self.player.setScale(3)
		self.player.setH(90)
		self.player.reparentTo(render)
		
		self.weapon = GattlingGun(0, 0, 800, 0, [])
		self.weapon.form.reparentTo(self.player)
		
		self.env = loader.loadModel("models/environment")
		self.env.reparentTo(render)
		self.env.setScale(.25)
		
	def	setupLights(self):
		#ambient light
		self.ambientLight = AmbientLight("ambientLight")
		#four values, RGBA (alpha is largely irrelevent), value range is 0:1
		self.ambientLight.setColor((.25, .25, .25, 1))
		self.ambientLightNP = render.attachNewNode(self.ambientLight)
		#the nodepath that calls setLight is what gets illuminated by the light
		render.setLight(self.ambientLightNP)
		#call clearLight() to turn it off
		
		self.keyLight = DirectionalLight("keyLight")
		self.keyLight.setColor((.6,.6,.6, 1))
		self.keyLightNP = render.attachNewNode(self.keyLight)
		self.keyLightNP.setHpr(0, -26, 0)
		render.setLight(self.keyLightNP)
		self.fillLight = DirectionalLight("fillLight")
		self.fillLight.setColor((.4,.4,.4, 1))
		self.fillLightNP = render.attachNewNode(self.fillLight)
		self.fillLightNP.setHpr(30, 0, 0)
		render.setLight(self.fillLightNP)
		
		self.headlight = Spotlight("slight")
		self.headlight.setColor(VBase4(1, 1, .5, 1))
		lens = PerspectiveLens()
		lens.setFov(100)
		self.headlight.setLens(lens)
		slnp = self.player.attachNewNode(self.headlight)
		render.setLight(slnp)
		slnp.setPos(0, -650, 300)
		slnp.setHpr(0, 180, 0)
		self.headlight.showFrustum()
			
	def move(self, task):
		elapsed = task.time - self.prevtime
		camera.lookAt(self.player)
		if self.keyMap["left"]:
			self.player.setH(self.player.getH() + elapsed * 100)
		if self.keyMap["right"]:
			self.player.setH(self.player.getH() - elapsed * 100)
		if self.keyMap["forward"]:
			dist = elapsed * self.velocity
			self.velocity += elapsed * 20
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		if self.keyMap["down"]:
			dist = -5 * elapsed
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		if (self.keyMap["forward"]==0):
			dist = elapsed * self.velocity
			if self.velocity >= 0:
				self.velocity -= elapsed * 50
			if self.velocity < 0:
				self.velocity = 0
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		
		#light testing
		#self.lighttest.light.setPoint((self.player.getX(), self.player.getY(), self.player.getZ()+3))
		
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