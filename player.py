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
from weaponSpawn import *


class playerCheckpoint(ai_node):
	def __init__(self, x, y, z, i):
		ai_node.__init__(self, x, y, z, i)
		
	def loadModel(self):
		self.form = loader.loadModel("models/jack")
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		#self.cHandler.setInPattern('path-node-%fn')
		
		cSphere = CollisionSphere(0, 0, 0, 20)
		name_string = "checkpoint"+self.id
		print "generating checkpoint with name ", name_string, self.xpos, self.ypos, self.zpos
		cNode = CollisionNode(name_string)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		#if int(self.id) == 0:
		#cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
class player_node_handler(object):
	def __init__(self):
		self.path = []
		self.populate_nodes()
		
	def populate_nodes(self):
		#print os.getcwd()
#NOTE: you guys need to move path_nodes.txt into your panda python folder
		f = open("player_checkpoints.txt", "r")
		#read in nodes from file
		i = 1
		for line in f:
			words = line.split()
			self.path.append(playerCheckpoint(float(words[0]), float(words[1]), float(words[2]), str(i)))
			i += 1
		f.close()
		
	#for this one, we aren't recycling nodes, we're getting rid of them and generating a new one
	#in the same position but with a different id
	def checkpoint(self):
		print "player checkpoint!", self.path[0].id
		self.path.append(playerCheckpoint(self.path[0].form.getX(), self.path[0].form.getY(), self.path[0].form.getZ(), str(int(self.path[len(self.path)-1].id)+1)))
		self.path[0].form.removeNode()
		self.path.pop(0)
		
	def next(self):
		return [self.path[0].xpos, self.path[0].ypos, self.path[0].zpos, self.path[0].id]

class Player(DirectObject):
	def __init__(self, x, y, z):
	
		self.x = x
		self.y = y
		self.z = z
		self.lastz = z
		#self.f = open("new_ai_nodes.txt", "w")

		self.pointX = x
		self.pointY = y
		
		self.timer = 30.0

		
		
		self.loadModels()
		self.setupLights()
		self.collisionInit()
		self.HUD = HUD()
		self.checkpointCount = 0
		self.laps = 0
		self.totalDist = 0
		self.distanceLeft = 1000
		self.place = 0
		

		self.keyMap = {"left":0, "right":0, "forward":0, "down":0, "break":0, "test":0}

		taskMgr.add(self.move, "moveTask")
		taskMgr.add(self.updateHUD, "hudTask")
		self.prevtime = 0
		self.velocity = 0
		self.topspeed = 70
		self.worldspeed = 1
		self.penalty = 0
		self.id = 0
		self.invincible = False
		self.gravity = 5
		
		#handle checkpoints
		self.checkpoints = player_node_handler()
		self.goal = self.checkpoints.next()

		self.last_checkpoint = self.goal

		self.distance = math.sqrt((self.goal[0] - self.pointX)**2+(self.goal[1] - self.pointY)**2)

		self.env = 0
		#jumping 'n' such
		self.stopped = True
		self.airborne = False
		
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
		#self.accept("collide-wall", self.putPlayer)
		#add an acceptor for the first checkpoint
		self.accept("collide-checkpoint1", self.checkpoint)
		#self.accept("collide-oil-slick", self.oil_slicked)
		#self.accept("collide-spikes", self.spiked)
		self.accept("collide-gatSpawn", self.changeWeapons, [0])
		self.accept("collide-bombSpawn", self.changeWeapons, [1])	
	
	def changeWeapons(self, wepIndex, cEntry):
		if(wepIndex == 0):
			self.weapon = Weapon(0,0,-3,0,self.weapon.bullets,0,self.z+3)
			players.spawns[0].collectable = False
			players.spawns[0].setDowntime()
			cEntry.getIntoNodePath().remove()
		elif(wepIndex == 1):
			self.weapon = BombWeapon(0,0,0,0,self.weapon.bullets,0,self.z)
			players.spawns[1].collectable = False
			players.spawns[1].setDowntime()
			cEntry.getIntoNodePath().remove()
			
	
	#triggers when the player his next checkpoint
	def checkpoint(self, cEntry):
		if cEntry.getIntoNodePath().getName() == "checkpoint" + str(self.goal[3]):
			self.last_checkpoint = self.goal
			self.pointX = self.goal[0]
			self.pointY = self.goal[1]
			self.checkpoints.checkpoint()
			self.timer += 25.0
			if (int(self.goal[3])-1)%4==3:
				self.gravity = 25
				print "changing gravity to ", self.gravity
			elif (int(self.goal[3])-1)%4==2:
				self.gravity = 2.5
			else:
				self.gravity = 10
			self.goal = self.checkpoints.next()
			self.distance = math.sqrt((self.goal[0] - self.pointX)**2+(self.goal[1] - self.pointY)**2)
			print("checkpoint")
			self.checkpointCount += 1
			if self.checkpointCount >= 5:
				self.checkpointCount = 0
				self.laps += 1
			#add an acceptor for our next checkpoint
			self.accept("collide-checkpoint" + str(self.goal[3]), self.checkpoint)
			print "checkpoint!", str(self.goal[3])
	
	def loadModels(self):
		#self.panda = Actor("models/panda-model", {"walk":"panda-walk4", "eat":"panda-eat"})
		self.player = Actor("animations/gentlemanBike_idle", {"pedal":"animations/gentlemanBike_idle"})
		#self.player.loop('pedal')
		self.player.setScale(4.5)
		self.player.setPos(0, 0, -30)
		self.player.setH(-180)
		self.player.reparentTo(render)
		self.player.setPos(self.x,self.y,self.z)

		self.weapon = GattlingGun(0, 0, -3, 0, [], 0, self.z+3)
		#self.weapon = Weapon(0, 0, -3, 0, [], 0, self.z)
		#self.weapon = GattlingGun(0, 0, 800, 0, [], 0)
		#self.weapon = Weapon(0, 0, 600, 0, [], 0)

		#self.weapon = GattlingGun(0, 0, 0, self.player.getH(), [], 0)

		#self.weapon = GattlingGun(0, 0, 0, 0, [], 0, self.z+3)
		

		#self.weapon = BombWeapon(0, 0, -30, 0, [], 0, self.z)
		
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
		slnp.setPos(0, -2, 2)
		slnp.setHpr(0, 200, 0)
		self.headlight.showFrustum()
		
	def move(self, task):
		elapsed = task.time - self.prevtime
		startzed = self.player.getZ()
		if(self.penalty == 0):
			
			#testing jumping
			startP = self.player.getP()
			startP = -startP
			if -startP > 0:
				self.player.setP(-startP + 5*elapsed)
			#print "TESTING:", self.player.getP()
			
			if self.keyMap["left"]:
				self.player.setH(self.player.getH() + elapsed * 45)
			if self.keyMap["right"]:
				self.player.setH(self.player.getH() - elapsed * 45)
			if self.keyMap["test"]:
				#self.f.write(str(self.player.getX()) + ' ' + str(self.player.getY()) + ' ' + str(self.player.getZ()) +'\n')
				print "\tDEBUGGING!!!", self.player.getX(), self.player.getY(), self.player.getZ()
			#only allow them to accelerate if they are on the ground
			if self.keyMap["forward"] and not self.airborne:
				dist = elapsed * self.velocity
				self.velocity += elapsed * 20 * self.worldspeed
				if self.velocity > self.topspeed: self.velocity = self.topspeed
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ())
			elif self.keyMap["down"]:
				dist = elapsed * self.velocity
				self.velocity -= elapsed * 5
				if self.velocity < -10:
					self.velocity = -10
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ())
			if self.keyMap["break"]:
				dist = elapsed * self.velocity
				self.velocity -= elapsed *75
				if self.velocity < 0:
					self.velocity = 0
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ())
			if self.keyMap["forward"]==0 or self.airborne:
				dist = elapsed * self.velocity
				if self.velocity > 0 and not self.airborne:
					self.velocity -= elapsed * 5 * self.worldspeed
					if self.velocity < 0: self.velocity = 0
					#if self.velocity > self.topspeed: self.velocity = self.topspeed
				angle = deg2Rad(self.player.getH())
				dx = dist * math.sin(angle)
				dy = dist * -math.cos(angle)
				dz = 0
				if self.airborne:
					otherangle = deg2Rad(-self.player.getP())
					dz = dist * math.sin(otherangle)
					#dy += dist* -math.cos(otherangle)
					#print "dz is ", dz
				self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ()+dz)
				# if self.keyMap["down"]==0:
					# if self.velocity < 0:
						# dist = elapsed * self.velocity
						# self.velocity -= elapsed * 10
						# if self.velocity > 0:
							# self.velocity = 0
						# angle = deg2Rad(self.player.getH())
						# dx = dist * math.sin(angle)
						# dy = dist * -math.cos(angle)
						# self.player.setPos(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ())
			
		self.penalty -= elapsed
		if(self.penalty < 0):
			self.penalty = 0
			self.invincible = False
			
		startzed = self.player.getZ()
		
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
		
		live = self.weapon.update(self.player.getX(), self.player.getY(), self.weapon.form.getZ(), deg2Rad(self.player.getH()), elapsed)

		if(not live):
			self.weapon = Weapon(0,0,-30,0,self.weapon.bullets, self.id, self.z+3)
		#self.weapon.update(self.player.getX(), self.player.getY(), self.weapon.form.getZ(), deg2Rad(self.player.getH()), elapsed)
		
		self.playerColNp.setPos(self.player.getX(), self.player.getY(), self.player.getZ())
		
		base.cTrav.traverse(render)
		
		#deal with terrain collisions (ty Roaming Ralph)
		entries = []
		pitflag = False
		for i in range(self.playerHandler.getNumEntries()):
			entry = self.playerHandler.getEntry(i)
			if self.playerHandler.getEntry(i).getIntoNode().getName()=="path_collider":
				entries.append(entry)
			if self.playerHandler.getEntry(i).getIntoNode().getName()=="pit":
				pitflag = True
			#print(entry.getIntoNode().getName())
			#print(entry.getFromNode().getName())
			
		entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		if (len(entries) > 0) and (entries[0].getIntoNode().getName() == "path_collider"):
			if (len(entries) > 1) and (entries[1].getIntoNode().getName() == "terrain_collider"):
				print "other level detected: ", entries[0].getSurfacePoint(render).getZ(), entries[1].getSurfacePoint(render).getZ()
			#if our Z is greater than terrain Z, make player fall
			if self.player.getZ() > entries[0].getSurfacePoint(render).getZ():
				self.player.setZ(startzed-self.gravity*elapsed)
				self.player.setP(self.player.getP()+elapsed)
				
				if self.player.getP() > 25:
					self.player.setP(25)
				self.airborne = True
				#print "falling...new Z is ", self.player.getZ(), "heading is ", self.player.getP()
				#print "offset is ", 1*elapsed
			#if our Z is less than terrain Z, change it
			if self.player.getZ() < entries[0].getSurfacePoint(render).getZ():
				self.ramp = entries[0].getIntoNodePath()
				if self.velocity > 5:
					self.player.setP(self.ramp.getP())
					self.velocity -= 5*elapsed
				self.player.setZ(entries[0].getSurfacePoint(render).getZ())
				self.airborne = False
				#print "bumping up from ", startzed, " to ", self.player.getZ()
				#print "(", self.player.getX(), ",", self.player.getY(), ") (", entries[0].getSurfacePoint(render).getX(),",",entries[0].getSurfacePoint(render).getY(),")"
				#print "not falling..."
			#self.player.setZ(entries[0].getSurfacePoint(render).getZ())
			
		elif not pitflag:
			self.player.setZ(startzed-self.gravity*elapsed)
			self.player.setP(0)
			print "no collision", self.player.getZ()
			self.airborne = False
			self.player.setPos(self.last_checkpoint[0], self.last_checkpoint[1], self.last_checkpoint[2])
			# self.player.setH(0)
			# self.player.setP(0)
			self.velocity = 0
			self.take_damage(2)
		else:
			self.player.setZ(startzed-self.gravity*elapsed)
			self.player.setP(0)
			
		
		
		######deal with camera
		offset = self.player.getP()
		if offset > 15:
			self.player.setP(15)
			offset = 15
		elif offset < -15:
			self.player.setP(-15)
			offset = -15
		
		offset = deg2Rad(offset)
		camera.setP(0)
		yoffset = abs(math.cos(offset)*(25+(1*abs(self.velocity)/10))+math.sin(offset)*(3+(1*abs(self.velocity)/30)))
		zoffset = abs(math.cos(offset)*(3+(1*abs(self.velocity)/10))+math.sin(offset)*(3+(1*abs(self.velocity)/30)))
		######print "offset is ", offset, " yoffset is ", yoffset, " zoffzet is ", zoffset
		
		
		camera.setPos(0, yoffset, zoffset)
		#print "camera Z is ", camera.getZ(), zoffset
		camera.lookAt(self.player)
		camera.setP(camera.getP() + 7)
		
		
		self.prevtime = task.time
		self.lastz = self.player.getZ()
		self.timer -= elapsed
		return Task.cont
	
	#def adjustCamera(self, task):
		#camera.setPos(0, 25+10*self.velocity/15, 5)	
	#	return Task.cont
	
	def updateHUD(self, task):
		self.HUD.update(self.velocity, self.player.getX(), self.player.getY(), self.laps, self.place, self.timer)
		#self.distanceLeft -= self.getDist(self.player.getX(), self.player.getY(), self.goal)
		#self.HUD.updateMiniMap(self.player.getX(), self.player.getY())
		return Task.cont
		
	def collisionInit(self):
		base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 3)
		cNode = CollisionNode("player")
		cNode.addSolid(cSphere)
		#cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.player.attachNewNode(cNode)
		#cNodePath.show()
		
		#experiment with lifter
		self.playerRay = CollisionRay()
		self.playerRay.setOrigin(0, 0, 10)
		self.playerRay.setDirection(0, 0, -1)
		self.playerCol = CollisionNode('playerRay')
		self.playerCol.addSolid(self.playerRay)
		self.playerCol.setFromCollideMask(BitMask32.bit(0))
		self.playerCol.setIntoCollideMask(BitMask32.allOff())
		self.playerColNp = self.player.attachNewNode(self.playerCol)
		self.playerColNp.reparentTo(render)
		self.playerHandler = CollisionHandlerQueue()
		base.cTrav.addCollider(self.playerColNp, self.playerHandler)
		
		#pusher = CollisionHandlerPusher()
		
		#pusher.addCollider(cNodePath, self.player)
		#base.cTrav.addCollider(cNodePath, pusher)
		
		# pusher = CollisionHandlerPusher()
		# pusher.addCollider(cNodePath)
		# base.cTrav.addCollider(cNodePath, pusher)
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def take_damage(self, amount):
		if(not self.invincible):
			self.penalty += amount
			self.invincible = True
		
	def setKey(self,key,value):
		self.keyMap[key] = value
		
	def getDist(self, x, y, checkpoint, distance):
		cx = checkpoint[0]
		cy = checkpoint[1]
		dist = math.sqrt((cx-x)**2 + (cy-y)**2)
		
		if x != 0:
			rotAngle = math.atan(-y/x)
		else:
			rotAngle = math.pi/2
		
		newX = x*math.cos(rotAngle) - y*math.sin(rotAngle)
		
		#dToCheckpoint = dist - newX
		dToCheckpoint = distance - dist
	
		return dToCheckpoint
