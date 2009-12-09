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
    def __init__(self, pos,room):
        self._load_models(pos,room)
        self._setup_catcher_collisions()

    def _load_models(self, pos,room):
        self._model = loader.loadModel("models/breakblock")
        self._model.setPos(pos[0], pos[1], pos[2])
        self._model.reparentTo(room)
    def _setup_catcher_collisions(self):
        self._coll_trav = CollisionTraverser()
        # Player collision
        self._player_handler = CollisionHandlerQueue()
        self._player = CollisionSphere(0, -5, 0, 3)
        self._player_coll = CollisionNode('collision-breakblock')
        self._player_coll.addSolid(self._player)
        self._player_coll.setFromCollideMask(BitMask32.bit(7))
        self._player_coll.setIntoCollideMask(BitMask32.bit(7))
        self._player_coll_path = self._model.attachNewNode(self._player_coll)
        self._player_coll_path.show()
        self._coll_trav.addCollider(self._player_coll_path, self._player_handler)
        
