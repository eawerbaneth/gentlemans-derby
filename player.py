import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random
from weapons import *
from helper import *
from ai import *
from hud import *


class playerCheckpoint(ai_node):
	def __init__(self, x, y, i):
		ai_node.__init__(self, x, y, i)
		
	def loadModel(self):
		self.form = loader.loadModel("models/jack")
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, -30)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		#self.cHandler.setInPattern('path-node-%fn')
		
		cSphere = CollisionSphere(0, 0, 0, 10)
		name_string = "checkpoint"+self.id
		cNode = CollisionNode(name_string)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		#cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
class player_node_handler(object):
	def __init__(self):
		self.path = []
		self.populate_nodes()
		
	def populate_nodes(self):
		#print os.getcwd()
#NOTE: you guys need to move path_nodes.txt into your panda python folder
		f = open("test_track.txt", "r")
		#read in nodes from file
		for line in f:
			words = line.split()
			self.path.append(playerCheckpoint(int(words[0]), int(words[1]), words[2]))
		f.close()
		
	#for this one, we aren't recycling nodes, we're getting rid of them and generating a new one
	#in the same position but with a different id
	def checkpoint(self):
		print "player checkpoint!", self.path[0].id
		self.path.append(playerCheckpoint(self.path[0].form.getX(), self.path[0].form.getY(), str(int(self.path[len(self.path)-1].id)+1)))
		self.path[0].form.removeNode()
		self.path.pop(0)
		
	def next(self):
		return [self.path[0].xpos, self.path[0].ypos, self.path[0].id]

class Player(DirectObject):
	def __init__(self, x, y, z):
		self.loadModels()
		self.setupLights()
		self.collisionInit()
		self.HUD = HUD()
		
		self.keyMap = {"left":0, "right":0, "forward":0, "down":0, "break":0, "test":0}
		taskMgr.add(self.move, "moveTask")
		taskMgr.add(self.adjustCamera, "cameraTask")
		taskMgr.add(self.updateHUD, "hudTask")
		self.prevtime = 0
		self.velocity = 0
		self.topspeed = 30
		self.worldspeed = 1
		self.penalty = 0
		self.id = 0
		#handle checkpoints
		self.checkpoints = player_node_handler()
		self.goal = self.checkpoints.next()
		self.env = 0
		self.stopped = True
		
		self.accept("escape", sys.exit)
		self.accept("arrow_up", self.setKey, ["forward", 1])
		self.accept("arrow_right", self.setKey, ["right", 1])
		self.accept("arrow_left", self.setKey, ["left", 1])
		self.accept("arrow_down", self.setKey, ["down", 1])
		self.accept("z", self.setKey, ["break", 1])
		self.accept("w", self.setKey, ["test", 1])
		self.accept("arrow_up-up", self.setKey, ["forward", 0])
		self.accept("arrow_right-up", self.setKey, ["right", 0])
		self.accept("arrow_left-up", self.setKey, ["left", 0])
		self.accept("arrow_down-up", self.setKey, ["down", 0])
		self.accept("z-up", self.setKey, ["break", 0])
		self.accept("w-up", self.setKey, ["test", 0])
		self.accept("collide-wall", self.putPlayer)
		#add an acceptor for the first checkpoint
		self.accept("collide-checkpoint1", self.checkpoint)
	
	#triggers when the player his next checkpoint
	def checkpoint(self, cEntry):
		if cEntry.getIntoNodePath().getName() == "checkpoint" + str(self.goal[2]):
			self.checkpoints.checkpoint()
			self.goal = self.checkpoints.next()
			#add an acceptor for our next checkpoint
			self.accept("collide-checkpoint" + str(self.goal[2]), self.checkpoint)
	
	def loadModels(self):
		#self.panda = Actor("models/panda-model", {"walk":"panda-walk4", "eat":"panda-eat"})
		self.player = Actor("models/bikeExport", {"pedal":"models/bikeExport"})
		#self.player.loop('pedal')
		#self.player.setScale(.005)
		self.player.setPos(0, 0, -30)
		self.player.setH(-180)
		self.player.reparentTo(render)
		
		#self.weapon = GattlingGun(0, 0, 0, self.player.getH(), [], 0)
		self.weapon = BombWeapon(0, 0, -30, 0, [], 0)
		self.weapon.form.reparentTo(self.player)
		self.weapon.form.setPos(self.weapon.form.getX(), self.weapon.form.getY(), self.weapon.form.getZ()+ 3)
		#print "\t", self.weapon.form.getH(), self.player.getH()
	
	def putPlayer(self, cEntry):
		self.player.setPos(0,0,-30)	
	
	def setupLights(self):
		self.headlight = Spotlight("slight")
		self.headlight.setColor(VBase4(1, 1, .5, 1))
		lens = PerspectiveLens()
		lens.setFov(100)
		self.headlight.setLens(lens)
		slnp = self.player.attachNewNode(self.headlight)
		render.setLight(slnp)
		slnp.setPos(0, -1, 1)
		slnp.setHpr(0, 180, 0)
		self.headlight.showFrustum()
		
	def move(self, task):
		elapsed = task.time - self.prevtime
		startzed = self.player.getZ()
		camera.lookAt(self.player)
		
		
		if self.keyMap["left"]:
			self.player.setH(self.player.getH() + elapsed * 45)
		if self.keyMap["right"]:
			self.player.setH(self.player.getH() - elapsed * 45)
		if self.keyMap["test"]:
			print "\tDEBUGGING!!!", self.player.getX(), self.player.getY(), self.player.getZ()
		if self.keyMap["forward"]:
			dist = elapsed * self.velocity
			self.velocity += elapsed * 20 * self.worldspeed
			if self.velocity > self.topspeed: self.velocity = self.topspeed
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		elif self.keyMap["down"]:
			dist = elapsed * self.velocity
			self.velocity -= elapsed * 5
			if self.velocity < -10:
				self.velocity = -10
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		if self.keyMap["break"]:
			dist = elapsed * self.velocity
			self.velocity -= elapsed *75
			if self.velocity < 0:
				self.velocity = 0
			angle = deg2Rad(self.player.getH())
			dx = dist * math.sin(angle)
			dy = dist * -math.cos(angle)
			self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		if self.keyMap["forward"]==0:
			if self.velocity >= 0:
				dist = elapsed * self.velocity
				self.velocity -= elapsed * 50 * self.worldspeed
				if self.velocity < 0:
					self.velocity = 0
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		if self.keyMap["down"]==0:
			if self.velocity < 0:
				dist = elapsed * self.velocity
				self.velocity += elapsed * 50
				if self.velocity > 0:
					self.velocity = 0
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, 0)
		
		#control animation speed
		animControl = self.player.getAnimControl('pedal')
		if self.velocity == 0:
			#self.player.pose('pedal', animControl.getFrame())#, self.player.getCurrentFrame('pedal'))
			self.player.stop()
			self.stopped = True
		elif self.velocity > 0:
			if self.stopped:
				#print "starting again"
				self.player.setPlayRate(0.3, 'pedal')
				self.player.loop('pedal')
				#self.player.loop('pedal', restart = 0, fromFrame = self.player.getCurrentFrame('pedal'))
			else:
				self.player.setPlayRate(self.velocity/10, 'pedal')
			self.stopped = False
		else:
			if self.stopped:
				self.player.setPlayRate(-1, 'pedal')
				self.player.loop('pedal')
				#self.player.loop('pedal', restart = 0, fromFrame = self.player.getCurrentFrame('pedal'))
			self.stopped = False
		
		self.weapon.update(self.player.getX(), self.player.getY(), self.weapon.form.getZ(), deg2Rad(self.player.getH()), elapsed)
		
		base.cTrav.traverse(render)
		
		#deal with terrain collisions (ty Roaming Ralph)
		entries = []
		for i in range(self.playerHandler.getNumEntries()):
			entry = self.playerHandler.getEntry(i)
			entries.append(entry)
			#print(entry.getIntoNode().getName())
			
		#entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		if (len(entries) > 0) and (entries[0].getIntoNode().getName() == "courseOBJ:polySurface1"):
			#if our Z is greater than terrain Z, make player fall
			if self.player.getZ() > entries[0].getSurfacePoint(render).getZ():
				self.player.setZ(startzed-1*elapsed)
				#print "falling...new Z is ", self.player.getZ()
				#print "offset is ", 1*elapsed
			#if our Z is less than terrain Z, change it
			if self.player.getZ() < entries[0].getSurfacePoint(render).getZ():
				self.player.setZ(entries[0].getSurfacePoint(render).getZ())
				#print "not falling..."
			#self.player.setZ(entries[0].getSurfacePoint(render).getZ())
			
		else:
			self.player.setZ(startzed)
			print "no collision"
		
		self.prevtime = task.time
		return Task.cont
	
	def adjustCamera(self, task):
		camera.setPos(0, 25+10*self.velocity/15, 5)	
		return Task.cont
	
	def updateHUD(self, task):
		self.HUD.updateSpeed(self.velocity)
		return Task.cont
		
	def collisionInit(self):
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 3)
		cNode = CollisionNode("player")
		cNode.addSolid(cSphere)
		cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.player.attachNewNode(cNode)
		#cNodePath.show()
		
		#experiment with lifter
		self.playerRay = CollisionRay()
		self.playerRay.setOrigin(0, 0, 3)
		self.playerRay.setDirection(0, 0, -1)
		self.playerCol = CollisionNode('playerRay')
		self.playerCol.addSolid(self.playerRay)
		self.playerCol.setFromCollideMask(BitMask32.bit(0))
		self.playerCol.setIntoCollideMask(BitMask32.allOff())
		self.playerColNp = self.player.attachNewNode(self.playerCol)
		self.playerHandler = CollisionHandlerQueue()
		base.cTrav.addCollider(self.playerColNp, self.playerHandler)
		#self.playerHandler = CollisionHandlerFloor()
		#self.playerHandler.addCollider(self.playerColNp, self.player)
		#base.cTrav.addCollider(self.playerColNp, self.playerHandler)
		
		#self.ray = CollisionRay(0, 0, 1, 0, 0, -1)
		#self.playerRay = self.player.attachNewNode(CollisionNode('ray'))
		#self.playerRay.node().addSolid(self.ray)
		#self.playerColNp.show()
		
		# self.fromObject = self.player.attachNewNode(CollisionNode('floor_collider'))
		# self.fromObject.node().addSolid(CollisionRay(0, 0, 0, 0, 0, -1))
		
		# self.lifter = CollisionHandlerFloor()
		#lifter.addCollider(fromObject, self.player)
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def take_damage(self, amount):
		self.penalty += amount
		
	def setKey(self,key,value):
		self.keyMap[key] = value
