import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random
import os

class ai_node(object):
	def __init__(self, x, y, i):
		self.xpos = x
		self.ypos = y
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
		
		self.loadModel()
		self.setupCollision()
		
		taskMgr.add(self.update, "ai-update")
		self.prevtime = 0
	
	def loadModel(self):
		self.form = Actor("models/panda-model")
		self.form.setScale(.004)
		self.form.setH(90)
		self.form.reparentTo(render)
	
	def setupCollision(self):
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("ai" + str(self.id) + "-collide-%in")
		
		cSphere = CollisionSphere((0,0,0), 500)
		cNode = CollisionNode("ai"+str(self.id))
		cNode.addSolid(cSphere)
		cNode.setIntoCollideMask(BitMask32.allOff())
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		
		for i in self.brain.path:
			self.accept("ai" + str(self.id) + "-collide-ai-node"+ i.id, self.checkpoint)
		
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def checkpoint(self, cEntry):
		print "checkpoint!"
		if cEntry.getIntoNodePath().getName() == "ai-node" + str(self.goal[2]):
			self.brain.checkpoint()
			self.goal = self.brain.next()
			print self.goal[0], self.goal[1], self.goal[2]
	
	def update(self, task):
		elapsed = task.time - self.prevtime
		angle = rad2Deg(math.atan2((self.form.getY()-self.goal[1]), (self.form.getX()-self.goal[0])) - math.pi/2)
		cur_heading = self.form.getH()
		
		if abs(angle - cur_heading) > 45 and abs(angle - cur_heading+360) > 45:
			#get ai turning in the correct direction
			#if abs(angle - cur_heading) > 180:
			self.form.setH(cur_heading + ((angle-cur_heading)%360)*elapsed)
			#else:
			#	self.form.setH(cur_heading + ((angle-cur_heading)%360)*elapsed)
		
			#SLOW DOWN FOR TURNS
			if abs(angle - cur_heading) > 90 and abs(angle - cur_heading+360) > 90:
				self.velocity = .8*self.velocity
			elif abs(angle - cur_heading) > 60 and abs(angle - cur_heading+360) > 60:
				self.velocity = .95*self.velocity
			#if self.velocity > 15:
			#	self.velocity -= elapsed * 30 #(1/self.velocity**2)*elapsed
			#elif self.velocity > 10:
			#	self.velocity -= elapsed * 25
			#elif self.velocity > 5:
			#	self.velocity -= elapsed * 15
			
		else:
			self.form.setH(angle)
		
		dist = elapsed*self.velocity
		self.velocity += elapsed * 20
		if self.velocity > self.topspeed:
			self.velocity = self.topspeed
		dx = dist* math.sin(deg2Rad(self.form.getH()))
		dy = dist*-math.cos(deg2Rad(self.form.getH()))
		self.form.setPos(self.form.getX() + dx, self.form.getY()+dy, 0)
		
		self.prevtime = task.time
		return Task.cont
		
	
	
	
