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

    def _load_models(self, pos):
        self._model = Actor("models/cat")
        self._model.setScale(1 * settings.GLOBAL_SCALE)
        self._model.setPos(pos[0], pos[1], pos[2])
        self._model.reparentTo(render)
