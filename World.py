import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import * #basic Panda modules
from direct.showbase.DirectObject import DirectObject #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import * #for compound intervals
from direct.task import Task #for update functions
import sys, math, random, os
from weapons import *
from ai import *
from helper import *
from player import *
from weaponSpawn import *
from menu import *
from misc import StreetLamp

class World(DirectObject):
	def __init__(self):
		base.disableMouse()
		camera.setPosHpr(0, -15, 7, 0, -15, 0)

		players.add_player(Player(17, -100, -30))
		
		players.add_spawn(gatSpawn(-105, -10, -10))
		players.add_spawn(bombSpawn(228,-341,-10))
		
		self.lights = []
		
		self.loadModels()
		self.setupLights()
		self.setupCollisions()
		#self.worldMusic = loader.loadSfx("Sound/Music/entertainer.mp3")
		#self.worldMusic.play()
		taskMgr.add(self.getPlace, "placeTask")
		
		#render.setShaderAuto()
		
	#def changeWeapons(self, cEntry):
	#	self.weapon = GattlingGun(0,0,0,0,self.weapon.bullets)
		

	def loadModels(self):
		#self.env = loader.loadModel("models/intermediate_course_export")
		#cNode = self.env.find("**/terrain_collider")
		#cNode.show()
		#self.env = loader.loadModel("models/easy_course")
		self.env = loader.loadModel("models/courseFixExport")
		#cNode = self.env.find("**/terrain_collider")
		#cNode.show()
		

		self.env.reparentTo(render)
		self.env.setPos(self.env.getX(), self.env.getY(), self.env.getZ()-30)
		
		#self.oil = oilSlick(32, 50, -30)
		#self.spikes = Spikes(32, 40, -30)
		
		#read in nodes from file
		for x in range(1, 5):
			ainodes = open("new_ai_nodes.txt", "r")
			path = []
			i = 0
			for line in ainodes:
				words = line.split()
				path.append(ai_node(float(words[0]), float(words[1]), float(words[2]), str(i)))
				i +=1
			players.add_player(ai_player(x, path))
			ainodes.close()
		
		
		
		#players.add_player(ai_player(1, path))
		#players.add_player(ai_player(2, path))
		#players.add_player(ai_player(3, path))
		#players.add_player(ai_player(4, path))

		self.env.setScale(8)
		camera.reparentTo(players.players[0].player)
		#camera.reparentTo(players.players[1].form)
		
		players.players[0].env = self.env

		camera.setPos(0, 4, 1)

	def setupCollisions(self):
		
		#base.cTrav = CollisionTraverser()
		cNode = self.env.find("**/pit")
		cNode.show()
		
		self.cHandler = CollisionHandlerEvent()
		
		
		#self.cHandler.setInPattern("%in-collide")
		#cSphere = CollisionInvSphere((0,0,0), 1)
		#cNode = CollisionNode("wall")
		#cNode.addSolid(cSphere)
		#cNodePath = self.env.attachNewNode(cNode)
		#cNodePath.show()

		#envCol = CollisionNode("floor")
		#envCol.setFromCollideMask(BitMask32.bit(0))
		#test = CollisionPolygon(Point3(0, 0, 0), Point3(50, 0, 50), Point3(50, 1, 50), Point3(0, 1, 0))
		#envCol.addSolid(test)
		#envCol.setIntoCollideMask(BitMask32.allOff())
		#nodepath = self.env.attachNewNode(envCol)
		#nodepath.show()
		#cSphere = CollisionInvSphere((0,0,0), 200)
		#cNode = CollisionNode("wall")
		#cNode.addSolid(cSphere)
		#cNodePath = self.env.attachNewNode(cNode)
		#cNodePath.show()

		
		#self.env.setCollideMask(BitMask32.allOff())
		
		#players.players[0].lifter.addCollider(players.players[0].fromObject, self.env)
		
		#do collision with ground
		#self.floor = CollisionHandlerFloor()
		#base.cTrav.addCollider(players.players[0].playerRay, self.floor)
		#self.floor.addCollider(players.players[0].playerRay, players.players[0].player)
		
		#base.cTrav.addCollider(cNodePath, self.cHandler)
		
		
	def loadLamps(self):
		#NOTE: you guys need to move lights.txt into your panda python folder
		f = open("new_ai_nodes.txt", "r")
		#read in nodes from file
		i=0
		for line in f:
			#print "creating new light"
			words = line.split()
			if i%3==0:
				self.lights.append(StreetLamp(float(words[0])+10, float(words[1])+10, float(words[2])))
			i += 1
		f.close()
		
	def	setupLights(self):
		## ambient light
		self.ambientLight = AmbientLight("ambientLight")
		## four values, RGBA (alpha is largely irrelevent), value range is 0:1
		self.ambientLight.setColor((.2, .1, .1, 1))
		self.ambientLightNP = render.attachNewNode(self.ambientLight)
		## the nodepath that calls setLight is what gets illuminated by the light
		render.setLight(self.ambientLightNP)
		## call clearLight() to turn it off
		
		self.loadLamps()
		
		self.keyLight = DirectionalLight("keyLight")
		self.keyLight.setColor((.2,.1,.7, 1))
		self.keyLightNP = render.attachNewNode(self.keyLight)
		self.keyLightNP.setHpr(0, -26, 0)
		render.setLight(self.keyLightNP)
		
		self.fillLight = DirectionalLight("fillLight")
		self.fillLight.setColor((.5,.3,.1, 1))
		self.fillLightNP = render.attachNewNode(self.fillLight)
		self.fillLightNP.setHpr(30, 0, 0)
		render.setLight(self.fillLightNP)
		
		# self.headlight = Spotlight("slight")
		# self.headlight.setColor(VBase4(1, 1, .5, 1))
		# lens = PerspectiveLens()
		# lens.setFov(100)
		# self.headlight.setLens(lens)
		# slnp = self.player.attachNewNode(self.headlight)
		# render.setLight(slnp)
		# slnp.setPos(0, -650, 300)
		# slnp.setHpr(0, 180, 0)
		# self.headlight.showFrustum()


	# def adjustCamera(self, task):
		# camera.setPos(0, 4000+4000*self.velocity/100, 1500)	
		# return Task.cont
		
	# def collisionInit(self):
		# base.cTrav = CollisionTraverser()
		# self.cHandler = CollisionHandlerEvent()
		# self.cHandler.setInPattern("collide-%in")
		
		# cSphere = CollisionSphere((0,0,0), 500)
		# cNode = CollisionNode("player")
		# cNode.addSolid(cSphere)
		# cNode.setIntoCollideMask(BitMask32.allOff())
		# cNodePath = self.player.attachNewNode(cNode)
		# cNodePath.show()
		
		# base.cTrav.addCollider(cNodePath, self.cHandler)
		
		# cSphere = CollisionInvSphere((0,0,0), 200)
		# cNode = CollisionNode("wall")
		# cNode.addSolid(cSphere)
		# cNodePath = self.env.attachNewNode(cNode)
		# cNodePath.show()

	def getPlace(self, task):
		#print players.players[0].timer
		p1 = players.players[0]
		p1.distanceLeft -= p1.getDist(p1.player.getX(), p1.player.getY(), p1.goal, p1.distance)
		players.players[1].distanceLeft -= p1.getDist(players.players[1].form.getX(), players.players[1].form.getY(), players.players[1].goal, players.players[1].distance)
		players.players[2].distanceLeft -= p1.getDist(players.players[2].form.getX(), players.players[2].form.getY(), players.players[2].goal, players.players[2].distance)
		players.players[3].distanceLeft -= p1.getDist(players.players[3].form.getX(), players.players[3].form.getY(), players.players[3].goal, players.players[3].distance)
		#players.players[4].distanceLeft -= p1.getDist(players.players[4].form.getX(), players.players[4].form.getY(), players.players[4].goal)
		
		L = [players.players[0].distanceLeft, players.players[1].distanceLeft, players.players[2].distanceLeft, players.players[3].distanceLeft]
		L.sort()
		
		players.players[0].place = L.index(players.players[0].distanceLeft)+1

	#"""print "Distance " +str(p1.getDist(players.players[1].form.getX(), players.players[1].form.getY(), players.players[1].goal))
	#	print "Distance " + str(players.players[1].distanceLeft)"""
		#print "Player distance " +str(players.players[1].distanceLeft)
		return Task.cont
		
	def destroy(self):
		taskMgr.remove("moveTask")
		taskMgr.remove("hudTask")
		taskMgr.remove("placeTask")
		taskMgr.remove("ai-update")
		taskMgr.remove("bombSpawnUpdate")
		taskMgr.remove("gatSpawnUpdate")
		
m = Menu()

#run()
while(True):
	taskMgr.step()
	if m.start == True:
		m.destroy()
		break
w = World()
endCond = False
while(True):
	taskMgr.step()
	if players.players[0].timer <= 0 or (players.players[0].laps == 3 and not players.players[0].place == 1):
		w.destroy()
		break
	elif players.players[0].timer > 0 and players.players[0].laps == 3 and players.players[0].place == 1:
		endCond = True
		w.destroy()
		break
		
e = EndScreen(endCond)
while(True):
	taskMgr.step()
