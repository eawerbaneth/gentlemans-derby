import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class Spikes(DirectObject):
	def __init__(self, x, y, z):
		#set position, start lowered
		self.mode = 0
		self.xpos = x
		self.ypos = y
		self.zpos = z
		self.loadModel()
		self.setupCollisions()
		self.prevtime = 0
		self.penalty = 4
		taskMgr.add(self.update, "spike_update")
		
	def loadModel(self):
		"""loads the spikes"""
#FLAG: waiting on spikes model
		self.form = loader.loadModel("models/panda-model")
		self.form.setScale(.02)
		self.form.reparentTo(render)
		
	def setupCollisions(self):
		#base.cTrav = CollisionTraverser()
		self.cHandler = CollisionHandlerEvent()
		self.cHandler.setInPattern("spiked-%in")
		
		cQuad = CollisionPolygon(Point3(0, 0, 0), Point3(0, 0, 10), Point3(0, 10, 10), Point3(0, 10, 0))
		cNode = CollisionNode("spikes")
		cNode.addSolid(cQuad)
		cNodePath = self.form.attachNewNode(cNode)
		base.cTrav.addCollider(cNodePath, self.cHandler)
		
	def update(self, task):
		elapsed = task.time - self.prevtime
		#if mode is 0, move up
		if self.mode == 0:
			self.form.setPos(self.form.getX(), self.form.getY(), self.form.getZ()+3*elapsed)
			#if we reach the top, set mode to 1
			if self.form.getZ() > self.zpos+10:
				self.mode = 1
		#else move down
		else:
			self.form.setPos(self.form.getX(), self.form.getY(), self.form.getZ()-3*elapsed)
			#if we reach the bottom, set mode to 0
			if self.form.getZ() < self.zpos-10:
				self.mode = 0
		
		self.prevtime = task.time
		return Task.cont
				