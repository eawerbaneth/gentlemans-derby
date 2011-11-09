from __future__ import division
import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
import sys, math, random
from weapons import *
from misc import *
from obstacles import *


class HUD():
    def __init__(self):
        self.speedometer = OnscreenImage(image = 'img/speedometerDial.png', pos = (-1, 0, -.7) )
        self.speedometer.setScale(.25)
        self.speedometer.setTransparency(TransparencyAttrib.MAlpha)
        self.speedPin = OnscreenImage(image = 'img/speedometerNeedle.png', pos = (-1, 0, -.7))
        self.speedPin.setScale(.15)
        self.speedPin.setTransparency(TransparencyAttrib.MAlpha)
        self.speedPin.setHpr(0, 0, 0)
        self.dot = OnscreenImage(image = 'img/dot.png', pos = (1, 0, -.7))
        self.dot.setScale(.025)
        self.lapText = OnscreenText(text = "0/10", pos = (1, -.3, 0), fg = (1, 1, 1, 1))
        self.lapText.setScale(.05)
        self.placeText = OnscreenText(text = "", pos = (1, -.4, 0), fg = (1, 1, 1, 1))
        self.placeText.setScale(.05)
        
    def update(self, velocity, x, y, laps, place):
        if velocity < 0:
            velocity = -velocity
        self.speedPin.setHpr(0, 0, 1.8*velocity)
        self.dot.setPos(1+(x/1500), 0, -.7+(y/1500))
        self.lapText.setText(str(laps)+"/10")
        self.placeText.setText(str(place) + "Place")
    
    """def getDist(self, x, y, checkpoint):
        cx = checkpoint[0]
        cy = checkpoint[1]
        dist = math.sqrt((cx-x)**2 + (cy-y)**2)
        
        rotAngle = math.atan2(-y,x)
        
        newX = x*math.cos(rotAngle) - y*math.sin(rotAngle)
        
        dToCheckpoint = dist - newX
        return dToCheckpoint"""
    
    """def updateMiniMap(self, x, y):
        self.dot.setPos(1+(x/1000), 0, -.7+(y/1000))"""
        
        