import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task
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
        self.position = pos
        self.destroyed = False

    def _load_models(self, pos,room):
        self._model = loader.loadModel("models/breakblock")
        self._model.setPos(pos)
        self._model.setScale(30)
        self._model.reparentTo(render)
        
    def getRoom(self):
        return self.number
    
    def getPosition(self):
        return self.position
    
    def destroyBlock(self):
        if not self.destroyed:
            self._model.removeNode()
            self.destroyed = True
        
