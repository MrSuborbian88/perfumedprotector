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

class Cat(enemy.Enemy):
    def __init__(self, pos,file_loc):
        enemy.Enemy.__init__(self, pos, file_loc)
        self._is_chase = False
        self._is_cat = True
        self._setup_cat_collision()

    def _load_models(self, pos):
        self._model = Actor("models/cat",{"enemove":"models/catanim.egg"})
        self._model.setScale(1 * settings.GLOBAL_SCALE)
        self._model.setPos(pos[0], pos[1], pos[2])
        self._model.reparentTo(render)
        
    def _setup_cat_collision(self):
        # Player sight target
        self._sphere_handler = CollisionHandlerQueue()
        self._sphere = CollisionSphere(0, 6, 0, 3)
        self._coll_sphere = CollisionNode('collision-enemy-sphere')
        self._coll_sphere.addSolid(self._sphere)
        self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
        self._coll_sphere.setIntoCollideMask(BitMask32.bit(6))
        self._coll_sphere_path = self._model.attachNewNode(self._coll_sphere)
        self._coll_sphere_path.show()
        self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)   
        # Player collision
        self._player_handler = CollisionHandlerQueue()
        self._player = CollisionSphere(0, 0, 0, 3)
        self._player_coll = CollisionNode('collision-with-player-cat')
        self._player_coll.addSolid(self._player)
        self._player_coll.setFromCollideMask(BitMask32.bit(7))
        self._player_coll.setIntoCollideMask(BitMask32.bit(7))
        self._player_coll_path = self._model.attachNewNode(self._player_coll)
        self._player_coll_path.show()
        self._coll_trav.addCollider(self._player_coll_path, self._player_handler)
