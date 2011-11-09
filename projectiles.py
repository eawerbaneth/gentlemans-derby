import sys, math, random, os
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
from helper import *
#from player import *

players = helper()

class Projectile(DirectObject):
	def __init__(self, vel, x, y, z, angle, range, playerid, id, penalty, playerList):
		self.xvel = vel*math.sin(angle)
		self.yvel = vel*-math.cos(angle)
		self.zvel = 0
		self.origx = x
		self.origy = y
		self.trajectory = angle
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.players = playerList
		#print(len(self.players.players))

		#self.loadModel()
		#self.setupCollisions()
		#self.prevtime = 0
		#self.range = range
		#self.penalty = penalty
		
		
		self.prevtime = 0
		self.range = range
		self.playerid = playerid
		self.id = id
		

		
		if(self.playerid == 0):
		
			self.accept("projectile:" + str(self.playerid) + ":" + str(self.id) + "-collide-ai1", self.kill, [1])
			self.accept("projectile:" + str(self.playerid) + ":" + str(self.id) + "-collide-ai2", self.kill, [2])
			self.accept("projectile:" + str(self.playerid) + ":" + str(self.id) + "-collide-ai3", self.kill, [3])
			self.accept("projectile:" + str(self.playerid) + ":" + str(self.id) + "-collide-ai4", self.kill, [4])
		else:
			self.accept("projectile:" + str(self.playerid) + ":" + str(self.id) + "-collide-player", self.kill, [0])
		
		self.loadModel()
		self.setupCollisions()
		
		#if self.playerid != 0:
		#	print "spawning projectile", self.playerid
		#if self.playerid != 0:
		#	self.accept("projectile:" + self.playerid + ":" + self.id + "-collide-player", self.kill)
		
		#for i in range(1:8):
		#	if i != int(self.playerid):
		#		self.accept("projectile:" + self.playerid + ":" + self.id + "-collide-ai" + str(i), self.kill)
			
	
	def loadModel(self):
		"""loads the bullet model"""
		#load the proxy model
		self.form = loader.loadModel("models/bullet")
		#self.form.setScale(.005)
		self.form.reparentTo(render)
	
	def setupCollisions(self):
		#run through the gambit
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		identifier = "projectile:" + str(self.playerid) + ":" + str(self.id)
		self.cHandler.setInPattern("%fn-collide-%in")
		
		#print(identifier)

		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode(identifier)

		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		
		self.bulletHandler = CollisionHandlerQueue()
		
		
		base.cTrav.addCollider(cNodePath, self.bulletHandler)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	#def update(self, task):
	def update(self, elapsed):
		"""moves the bullet in a straight line relative to its trajectory"""
		if(not self.form):
			return False
		#elapsed = task.time - self.prevtime
		self.xpos = self.xpos + self.xvel*elapsed
		self.ypos = self.ypos + self.yvel*elapsed
		self.form.setPos(self.xpos, self.ypos, self.zpos)
		
		for i in range(self.bulletHandler.getNumEntries()):
			entry = self.bulletHandler.getEntry(i)
			print(entry.getIntoNode().getName())
			print(entry.getFromNode().getName())
		
		#check to see if the projectile is out of range
		if math.sqrt((self.origx-self.xpos)**2 + (self.origy-self.ypos)**2) > self.range:
			 #kill the projectile
			 self.form.removeNode()
			 return False
		
		#self.prevtime = task.time
		#return Task.cont
		return True
			
	def kill(self, hitId, cEntry):
		"""destroys the bullet upon entering a foreign body"""

		#self.form.cleanup()
		#print(self.players.players[1])
		
		
		print("LOLOLOLOLOLOL")
		#print(self.players.players[hitId])
		self.players.players[hitId].take_damage(3)
		self.form.removeNode()
		#cEntry.getIntoNodePath().getParent().remove()

		#print(cEntry.getIntoNodePath().getName())
		#cEntry.getFromNodePath().getParent().remove()

	
class Flames(DirectObject):
	def __init__(self, x, y, z, angle):
		self.xpos = x + 100
		self.ypos = y + 100
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = -1
		#may need to play around with this value
		self.duration = 100
		self.penalty = 1
		
	def loadModel(self):
		"""loads the flame model"""
		#will likely need to change this to an actor
		self.form = loader.loadModel("models/panda-model")
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		"""sets up the flamebox to burn things"""
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('burned-up-%in')
		
		cSphere = CollisionSphere((0,0,0),3) 
		cNode = CollisionNode("flames")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
	
	def update(self, elapsed):
	#def update(self, task):
		"""the fire sticks around for a second and then disappears"""
		#elapsed = 0
		#if self.prevtime == -1:
		#	elapsed = 0
		#else:
		#	elapsed = task.time - self.prevtime
			
		self.duration -= elapsed
			
		if self.duration <= 0:
			self.form.removeNode()
			return False
		
		#	self.prevtime = task.time
		#	return Task.cont
		return True
	
class Bomb(DirectObject):
	def __init__(self, x, y, z, angle):
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.angle = angle
		self.loadModel()
		self.setupCollisions()
		self.prevtime = -1
		self.countdown = 3.0
		self.exploderange = 10.0
		self.penalty = 100
		self.exploded = False
		self.accept('bomb-detonated-player', self.explode)
		print "spawning bomb...", self.xpos, self.ypos, self.zpos
	
	def loadModel(self):
		"""loads the bomb model"""
		self.form = loader.loadModel("models/bombExport")
		self.form.reparentTo(render)
		self.form.setPos(self.xpos, self.ypos, self.zpos+3)
		
	def setupCollisions(self):
		"""sets the bomb up to collide with things"""
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern('bomb-detonated-%in')
		
		cSphere = CollisionSphere((0,0,0), 1)
		cNode = CollisionNode("bomb")
		cNode.addSolid(cSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def update(self, elapsed):
	#def update(self, task):
		"""the bomb sits until someone runs into it or its timer goes off"""
		#elapsed = 0
		#if self.prevtime == -1:
		#	elapsed = 0
		#else:
		#	elapsed = task.time - self.prevtime
		
		#camera.lookAt(self.form)
		
		self.countdown = self.countdown - elapsed
		print "bomb countdown: ", self.countdown
		
		if self.countdown <= 0 and not self.exploded:
			self.explode()
			
		if self.countdown <= -1:
			self.form.removeNode()
			return False
		
		#self.prevtime = task.time
		#return Task.cont
		return True
	
	#need to test to see if the explosion is lasting long enough to collide with anything
	#before being removed
	def explode(self):	
		"""the bomb explodes"""
		self.exploded = True
		#base.cTrav = CollisionTraverser()
		self.cHandler2 = CollisionHandlerEvent()
		self.cHandler2.setInPattern('blew-up-%in')
		
		explosionSphere = CollisionSphere(0, 0, 0, self.exploderange)
		cNode = CollisionNode("explosion")
		cNode.addSolid(explosionSphere)
		cNodePath = self.form.attachNewNode(cNode)
		cNodePath.show()
		base.cTrav.addCollider(cNodePath, self.cHandler2)
		