from __future__ import division
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TransparencyAttrib
import sys


class Menu(DirectObject):
    def __init__(self):
        self.title = OnscreenImage(image = 'img/titleScreen.png', pos = (0, 0, 0) )
        self.pointer = OnscreenImage(image = 'img/titleSelector.png', pos = (-.2, 0 ,-.63))
        self.pointer.setScale(.05)
        self.start = False
        self.instructions = False
        self.pointerPosition = 1
        self.pointer.setTransparency(TransparencyAttrib.MAlpha)
        
        self.accept("enter", self.screenHandler)
        self.accept("arrow_up", self.movePointerUp)
        self.accept("arrow_down", self.movePointerDown)
        self.accept("backspace", self.back)
        self.accept("escape", sys.exit)
        
    def screenHandler(self):
        if self.pointerPosition == 1:
            self.start = True
            self.title.destroy()
            self.pointer.destroy()
        else:
            self.instructions = True
            self.title.setImage('img/instructions.png')
            self.pointer.setAlphaScale(1)
            
    def back(self):
        if self.instructions == True:
            self.instructions = False
            self.title.setImage('img/titleScreen.png')
            self.pointer.setImage('img/titleSelector.png')
    
    def movePointerUp(self):
        if self.pointerPosition == 2:
            self.pointer.setPos(-.2, 0, -.63)
            self.pointerPosition = 1
    def movePointerDown(self):
        if self.pointerPosition == 1:
            self.pointer.setPos(-.2, 0, -.8)
            self.pointerPosition = 2
    def destroy(self):
        self.ignoreAll()
    
        

class EndScreen(DirectObject):
	def __init__(self, endState):
		if(endState):
			self.end = OnscreenImage(image = 'img/win_screen.png', pos = (0,0,0))
		else:
			self.end = OnscreenImage(image = 'img/lose_screen.png', pos = (0,0,0))
		self.accept("enter", sys.exit)
		
	def destroy(self):
		self.ignoreAll()