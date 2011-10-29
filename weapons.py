import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random

class Weapon(DirectObject):
	def __init__(self):
		self.keyMap = {"firing":0}
		self.prevtime = 0
		
		self.accept("space", self.setKey, ["firing", 1] )
		self.accept("space-up", self.setKey, ["firing", 0] )
	
	def setKey(self, key, value):
		self.keyMap[key] = value
	
	def fire(self, task):
		"""pull the trigger"""