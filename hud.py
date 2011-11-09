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
        self.speedPin.setScale(.10)
        self.speedPin.setTransparency(TransparencyAttrib.MAlpha)
        self.speedPin.setHpr(0, 0, 0)
        
        self.minimap = OnscreenImage(image = 'img/minimap.png', pos = (1.05, 0, -.65))
        self.minimap.setScale(.19, .19, .3)
        self.dot = OnscreenImage(image = 'img/dot.png', pos = (1.01, 0, -.55))
        self.dot.setScale(.025)
        
        #font1 = loader.loadFont('img/blackadder.TTF')
        #self.lapText = OnscreenText(text = "0/10", font = font1, pos = (1, -.3, 0), fg = (1, 1, 1, 1) )
        #self.lapText.setScale(.1)
        #self.placeText = OnscreenText(text = "", font = font1, pos = (1, -.4, 0), fg = (1, 1, 1, 1))
        #self.placeText.setScale(.1)
        #self.timerText = OnscreenText(text = "Time: ", font = font1, pos = (1, -.5, 0), fg = (1, 1, 1, 1))
        
    def update(self, velocity, x, y, laps, place, time):
        if velocity < 0:
            velocity = -velocity

        #self.dot.setPos(1.01+(x/4250), 0, -.55+(y/4250))
        #self.lapText.setText("Laps: " + str(laps)+"/10")

        self.speedPin.setHpr(0, 0, 4*velocity)


        #self.placeText.setText(str(place) + "Place")
        #self.timerText.setText("Time: "+ str(round(time)))
    
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
        
        