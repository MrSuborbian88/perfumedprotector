import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from pandac.PandaModules import BaseParticleEmitter,BaseParticleRenderer
from pandac.PandaModules import PointParticleFactory,SpriteParticleRenderer
import enemy

import settings
import math
import os
import random
import sys


class BreakBlock(DirectObject):
    def __init__(self, pos, room, number):
        self._load_models(pos,room)
        self.room = room
        self.number = number
        self.p = ParticleEffect()
        self.position = pos
        self.destroyed = False

    def _load_models(self, pos,room):
        self._model = loader.loadModel("models/breakblock")
        self._model.setPos(pos)
        self._model.setScale(50)
        self._model.reparentTo(render)
        
    def getRoom(self):
        return self.number
    
    def destroyBlock(self):
        if not self.destroyed:
            self._model.removeNode()
            #self.loadParticleConfig()
            self.destroyed = True
        
    def loadParticleConfig(self):
        self.p.cleanup()
        self.p = ParticleEffect()
        self.p.loadConfig(os.path.join("models", "smokering.ptf"))   
        self.p.accelerate(.25) 
        self.p.setPos(self.position) 
        self.p.reparentTo(render) 
        self.p.setScale(50)  
        self.p.start()
        #taskMgr.doMethodLater(5, self.cleanParticles, 'Stop Particles')
        
    def cleanParticles(self, random):
        self.p.softStop()
        
