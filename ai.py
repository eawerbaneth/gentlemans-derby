import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random
import os
from weapons import *
from helper import *

class ai_node(DirectObject):
	def __init__(self, x, y, i):
		self.xpos = x
		self.ypos = y
		self.id = i
		self.loadModel()
		self.setupCollisions()


		
	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, -30)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		#self.cHandler.setInPattern('path-node-%fn')
		
		cSphere = CollisionSphere(0, 0, 0, 5)
		name_string = "ai-node"+self.id
		cNode = CollisionNode(name_string)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		#cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)

		
class node_handler(DirectObject):
	def __init__(self):
		self.path = []
		
		#self.form.hide()
		self.populate_nodes()
		#self.populate_tubes()
		
	def populate_nodes(self):
		print os.getcwd()
#NOTE: you guys need to move path_nodes.txt into your panda python folder
		f = open("test_track.txt", "r")
		#read in nodes from file
		for line in f:
			words = line.split()
			self.path.append(ai_node(int(words[0]), int(words[1]), words[2]))
		f.close()
		
	#def populate_tubes(self):
	#	self.cHandler = CollisionHandlerEvent()
	#	self.cHandler.setInPattern("%fn-collide-%in")
	#	print(self.path[0].xpos)
	#	print(self.path[0].ypos)
		#print(self.path[0].zpos)
		
	#	print(self.path[1].xpos)
	#	print(self.path[1].ypos)
		#print(self.path[1].zpos)
		
	#	self.tubeHandler = CollisionHandlerQueue()
		#base.cTrav.addCollider(cNodePath, self.bulletHandler)
		
	#	for p in range(len(self.path)):
	#		if(p + 1 >= len(self.path)):
	#			cTube = CollisionTube(self.path[p].xpos, self.path[p].ypos, 0, self.path[0].xpos, self.path[0].ypos, 0, 10)
	#		else:
	#			cTube = CollisionTube(self.path[p].xpos, self.path[p].ypos, 0, self.path[p+1].xpos, self.path[p+1].ypos, 0, 10)
	#		cNode = CollisionNode("tube" + str(p))
	#		cNode.addSolid(cTube)
	#		print(cNode.getName())
	#		cNodePath = self.form.attachNewNode(cNode)
	#		cNodePath.show()
	#		base.cTrav.addCollider(cNodePath,self.cHandler)
	#		base.cTrav.addCollider(cNodePath, self.tubeHandler)

	
	def checkpoint(self):
		self.path.append(self.path.pop(0))
		
	def next(self):
		return [self.path[0].xpos, self.path[0].ypos, self.path[0].id]
		
class ai_player(DirectObject):
	def __init__(self, id):
		self.brain = node_handler()
		self.goal = self.brain.next()
		self.id = id
		self.velocity = 0
		self.topspeed = 30
		self.time_penalty = 0
		self.invincible = False
		
		self.loadModel()
		self.setupLights()
		self.setupCollision()
		self.handle = "ai" + str(id)
		
		taskMgr.add(self.update, "ai-update")
		self.prevtime = 0
	
	def setupLights(self):
		self.headlight = Spotlight("slight")
		self.headlight.setColor(VBase4(1, 1, .5, 1))
		lens = PerspectiveLens()
		lens.setFov(100)
		self.headlight.setLens(lens)
		slnp = self.form.attachNewNode(self.headlight)
		render.setLight(slnp)
		slnp.setPos(0, -1, 1)
		slnp.setHpr(0, 180, 0)
		#self.headlight.showFrustum()
	
	def loadModel(self):
		self.form = Actor("models/gentlemanBike_Pistol", {"pedal":"models/gentlemanBike_Pistol"})
		#self.form.setScale(.004)
		self.form.setH(45)
		self.form.loop('pedal')
		self.form.reparentTo(render)
		self.form.setPos(self.form.getX()+ int(self.id), self.form.getY() + int(self.id), -30)
		
		#load default weapon
		self.weapon = Weapon(0, 0, 600, 0, [], self.id, self.form.getZ())
		self.weapon.form.reparentTo(self.form)
		self.weapon.form.setPos(self.weapon.form.getX(), self.weapon.form.getY(), self.weapon.form.getZ()+3)
	
	def setupCollision(self):
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("ai" + str(self.id) + "-collide-%in")
		
		#keep ai rooted to the ground
		self.aiRay = CollisionRay()
		self.aiRay.setOrigin(0, 0, 3)
		self.aiRay.setDirection(0, 0, -1)
		self.aiCol = CollisionNode('aiRay')
		self.aiCol.addSolid(self.aiRay)
		self.aiCol.setFromCollideMask(BitMask32.bit(0))
		self.aiCol.setIntoCollideMask(BitMask32.allOff())
		self.aiColNp = self.form.attachNewNode(self.aiCol)
		self.aiHandler = CollisionHandlerQueue()
		base.cTrav.addCollider(self.aiColNp, self.aiHandler)
		
		cSphere = CollisionSphere((0,0,0), 3)
		cNode = CollisionNode("ai"+str(self.id))
		#print("ai"+str(self.id))
		cNode.addSolid(cSphere)
		#cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.form.attachNewNode(cNode)
		#cNodePath.show()
		
		#add acceptors
		for i in self.brain.path:
			self.accept("ai" + str(self.id) + "-collide-ai-node"+ i.id, self.checkpoint)
		self.accept("ai" + str(self.id) + "-collide-spikes", self.penalty)
		self.accept("ai" + str(self.id) + "-collide-oil-slick", self.oil_slicked)
		self.accept("ai" + str(self.id) + "-collide-gatSpawn", self.changeWeapons, [0])
		self.accept("ai" + str(self.id) + "-collide-bombSpawn", self.changeWeapons, [1])
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def changeWeapons(self, wepIndex, cEntry):
		if(wepIndex == 0):
			self.weapon = GattlingGun(0,0,0,0,self.weapon.bullets,0,3)
			players.spawns[0].collectable = False
			players.spawns[0].setDowntime()
			cEntry.getIntoNodePath().remove()
		elif(wepIndex == 1):
			self.weapon = BombWeapon(0,0,-30,0,[],0,0)
			players.spawns[1].collectable = False
			players.spawns[1].setDowntime()
			cEntry.getIntoNodePath().remove()
	
	def oil_slicked(self, cEntry):
		print "ai " + str(self.id) + " oil slicked!"
	
	def penalty(self, cEntry):
		if cEntry.getIntoNodePath().getName() == "spikes":
			self.take_damage(3)
		#if cEntry.getIntoNodePath().getName() == "
	
	def take_damage(self, amount):
		if(not self.invincible):
			self.time_penalty += amount
			self.invincible = True
	
	def checkpoint(self, cEntry):
		#print "checkpoint!"
		if cEntry.getIntoNodePath().getName() == "ai-node" + str(self.goal[2]):
			self.brain.checkpoint()
			self.goal = self.brain.next()
			#print self.goal[0], self.goal[1], self.goal[2]
	
	def update(self, task):
		elapsed = task.time - self.prevtime
		startzed = self.form.getZ()
		
		#jumping
		startP = self.form.getP()
		startP = -startP
		if -startP > 0:
			self.form.setP(-startP + 5*elapsed)
			startP = -(-startP + 5*elapsed)
		
		#if we're allowed to move, move
		if self.time_penalty == 0:
			angle = rad2Deg(math.atan2((self.form.getY()-self.goal[1]), (self.form.getX()-self.goal[0])) - math.pi/2)
			cur_heading = self.form.getH()
			cos_heading = self.form.getH()
			
			if abs(angle - cur_heading) > 25 and abs(angle - cur_heading+360) > 25:
				#get ai turning in the correct direction
				self.form.setH(cos_heading + ((angle-cur_heading)%360)*elapsed)

				#SLOW DOWN FOR TURNS
				if abs(angle - cur_heading) > 90 and abs(angle - cur_heading+360) > 90:
					self.velocity = .8*self.velocity
				elif abs(angle - cur_heading) > 60 and abs(angle - cur_heading+360) > 60:
					self.velocity = .95*self.velocity
				elif abs(angle - cur_heading) > 30 and abs(angle - cur_heading+360) > 30:
					self.velocity = .97*self.velocity
				elif abs(angle - cur_heading) > 15 and abs(angle - cur_heading+360) > 15:
					self.velocity = .99*self.velocity
			else:
				self.form.setH(angle)
			
			dist = elapsed*self.velocity
			self.velocity += elapsed * 20
			if self.velocity > self.topspeed:
				self.velocity = self.topspeed
			dx = dist* math.sin(deg2Rad(self.form.getH()))
			dy = dist*-math.cos(deg2Rad(self.form.getH()))
			self.form.setPos(self.form.getX() + dx, self.form.getY()+dy, 0)
		
		#reduce our penalty if we have one
		self.time_penalty -= elapsed
		if self.time_penalty < 0:
			self.time_penalty = 0
			self.invincible = False
			
		#print(len(players.players))	
		
		#update weapon
		shootflag = False
		if math.sqrt((self.form.getX() - players.players[0].player.getX())**2 + (self.form.getY() - players.players[0].player.getY())**2) < self.weapon.range + 5:
			shootflag = True
		for i in range(1, 5):
			if players.players[i].id != self.id:
				#check to see if anyone is in range, shoot if they are
				if math.sqrt((self.form.getX() - players.players[i].form.getX())**2 + (self.form.getY() - players.players[i].form.getY())**2) <= 30:
					shootflag = True
		self.weapon.setKey("firing", shootflag)
		
		
		live = self.weapon.update(self.form.getX(), self.form.getY(), self.weapon.form.getZ(), deg2Rad(self.form.getH()), elapsed) 
		
		if(not live):
			self.weapon = Weapon(0,0,-30,0,self.weapon.bullets, self.id, 3)
		
		#keep ai rooted to ground
		base.cTrav.traverse(render)
		
		#do animations
		animControl = self.form.getAnimControl('pedal')
		if self.velocity == 0:
			#self.player.pose('pedal', animControl.getFrame())#, self.player.getCurrentFrame('pedal'))
			self.form.stop()
			self.stopped = True
		elif self.velocity > 0:
			if self.stopped:
				#print "starting again"
				self.form.setPlayRate(0.3, 'pedal')
				self.form.loop('pedal')
				#self.player.loop('pedal', restart = 0, fromFrame = self.player.getCurrentFrame('pedal'))
			else:
				self.form.setPlayRate(self.velocity/10, 'pedal')
			self.stopped = False
		else:
			if self.stopped:
				self.form.setPlayRate(-1, 'pedal')
				self.form.loop('pedal')
				#self.player.loop('pedal', restart = 0, fromFrame = self.player.getCurrentFrame('pedal'))
			self.stopped = False
		
		#deal with terrain collisions
		entries = []
		for i in range(self.aiHandler.getNumEntries()):
			entry = self.aiHandler.getEntry(i)
			entries.append(entry)
			#print(entry.getIntoNode().getName())
			#print(entry.getFromNode().getName())
			
		#entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		if (len(entries) > 0) and (entries[0].getIntoNode().getName() == "courseOBJ:polySurface1"):
			#if our Z is greater than terrain Z, make player fall
			if self.form.getZ() > entries[0].getSurfacePoint(render).getZ():
				self.form.setZ(startzed-25*elapsed)
				self.form.setP(-startP + 5*elapsed)
				if self.form.getP() < 0:
					self.form.setP(0)
				#print "falling...new Z is ", self.form.getZ()
				#print "offset is ", 1*elapsed
			#if our Z is less than terrain Z, change it
			if self.form.getZ() < entries[0].getSurfacePoint(render).getZ():
				self.form.setZ(entries[0].getSurfacePoint(render).getZ())
				if self.velocity > 5:
					self.form.setP(-startP - 5*elapsed)
				#print "not falling..."
			#self.player.setZ(entries[0].getSurfacePoint(render).getZ())
			
		else:
			self.form.setZ(startzed)
			self.form.setP(0)
			#print "no collision"
		
		
		self.prevtime = task.time
		return Task.cont
		