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

class ai_node(object):
	def __init__(self, x, y, i):
		self.xpos = x + int(i)
		self.ypos = y + int(i)
		self.id = i
		self.loadModel()
		self.setupCollisions()

	def loadModel(self):
		self.form = loader.loadModel("models/teapot")
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, 0)
		
	def setupCollisions(self):
		self.cHandler = CollisionHandlerEvent()
		#self.cHandler.setInPattern('path-node-%fn')
		
		cSphere = CollisionSphere(0, 0, 0, 5)
		name_string = "ai-node"+self.id
		cNode = CollisionNode(name_string)
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
class node_handler(object):
	def __init__(self):
		self.path = []
		self.populate_nodes()
		
	def populate_nodes(self):
		print os.getcwd()
#NOTE: you guys need to move path_nodes.txt into your panda python folder
		f = open("path_nodes.txt", "r")
		#read in nodes from file
		for line in f:
			words = line.split()
			self.path.append(ai_node(int(words[0]), int(words[1]), words[2]))
		f.close()
		
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
		self.topspeed = 100
		self.time_penalty = 0
		
		self.loadModel()
		self.setupCollision()
		self.handle = "ai" + str(id)
		
		taskMgr.add(self.update, "ai-update")
		self.prevtime = 0
	
	def loadModel(self):
		self.form = Actor("models/panda-model")
		self.form.setScale(.004)
		self.form.setH(90)
		self.form.reparentTo(render)
		self.form.setPos(self.form.getX()+ int(self.id), self.form.getY() + int(self.id), self.form.getZ())
		
		#load default weapon
		self.weapon = Weapon(0, 0, 600, 0, [], self.id)
		self.weapon.form.reparentTo(self.form)
		self.weapon.form.setPos(self.weapon.form.getX(), self.weapon.form.getY(), self.weapon.form.getZ()+3)
	
	def setupCollision(self):
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("ai" + str(self.id) + "-collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 500)
		cNode = CollisionNode("ai"+str(self.id))
		cNode.addSolid(cSphere)
		cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		
		#add acceptors
		for i in self.brain.path:
			self.accept("ai" + str(self.id) + "-collide-ai-node"+ i.id, self.checkpoint)
		self.accept("ai" + str(self.id) + "-collide-spikes", self.penalty)
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def penalty(self, cEntry):
		if cEntry.getIntoNodePath().getName() == "spikes":
			self.take_damage(3)
		#if cEntry.getIntoNodePath().getName() == "
	
	def take_damage(self, amount):
		self.time_penalty += amount
	
	def checkpoint(self, cEntry):
		#print "checkpoint!"
		if cEntry.getIntoNodePath().getName() == "ai-node" + str(self.goal[2]):
			self.brain.checkpoint()
			self.goal = self.brain.next()
			#print self.goal[0], self.goal[1], self.goal[2]
	
	def update(self, task):
		elapsed = task.time - self.prevtime
		
		if self.time_penalty == 0:		
			angle = rad2Deg(math.atan2((self.form.getY()-self.goal[1]), (self.form.getX()-self.goal[0])) - math.pi/2)
			cur_heading = self.form.getH()
			
			if abs(angle - cur_heading) > 25 and abs(angle - cur_heading+360) > 25:
				#get ai turning in the correct direction
				self.form.setH(cur_heading + ((angle-cur_heading)%360)*elapsed)

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
		
		self.time_penalty -= elapsed
		if self.time_penalty < 0:
			self.time_penalty = 0
			
		#update weapon
		shootflag = False
		if math.sqrt((self.form.getX() - players.players[0].player.getX())**2 + (self.form.getY() - players.players[0].player.getY())**2) < self.weapon.range + 5:
			shootflag = True
		for i in range(1, 4):
			if players.players[i].id != self.id:
				#check to see if anyone is in range, shoot if they are
				if math.sqrt((self.form.getX() - players.players[i].form.getX())**2 + (self.form.getY() - players.players[i].form.getY())**2) <= 30:
					shootflag = True
		self.weapon.setKey("firing", shootflag)
		self.weapon.update(self.form.getX(), self.form.getY(), self.weapon.form.getZ(), deg2Rad(self.form.getH()), elapsed) 
		
		self.prevtime = task.time
		return Task.cont
		