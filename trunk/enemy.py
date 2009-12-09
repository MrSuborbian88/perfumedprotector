import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task

import settings
import math
import os
import random
import sys
import string


class Enemy(DirectObject):
    def __init__(self, pos, file_loc):
        self.dead=False
        self._is_moving=False
        self._is_chase=False
        self._is_cat=False
        self._tag = file_loc
        self._points = []
        self._load_models(pos)
        self._setup_collisions()
        self._setup_tasks()
        self._read_points(file_loc)
        self._current = self._points[0]
        self.gravity = 0
        self._walk_rate = 25

    def _load_models(self, pos):
        self._model = Actor(os.path.join('models', 'enemy'),
                {'enemove' : os.path.join('models', 'enemy_walk')})
        self._model.setScale(1 * settings.GLOBAL_SCALE)
        self._model.setPos(pos[0], pos[1], pos[2])
        #self._model.reparentTo(render)
        
    def _setup_collisions(self):
        self._coll_trav = CollisionTraverser()
        # Ground collision
        self._ground_handler = CollisionHandlerQueue()
        self._ground_ray = CollisionRay()
        self._ground_ray.setOrigin(1, 0, 0)
        self._ground_ray.setDirection(0, 0, -1)
        self._ground_coll = CollisionNode('collision-ground')
        self._ground_coll.addSolid(self._ground_ray)
        self._ground_coll.setFromCollideMask(BitMask32.bit(0))
        self._ground_coll.setIntoCollideMask(BitMask32.allOff())
        self._ground_coll_path = self._model.attachNewNode(self._ground_coll)
        #self._ground_coll_path.show()
        self._coll_trav.addCollider(self._ground_coll_path, self._ground_handler)
        # Sight collision (Mid)
        self._sight_handler_mi = CollisionHandlerQueue()
        #self._sight_ray_mi = CollisionRay()
        #self._sight_ray_mi.setOrigin(1, 0, 0)
        #self._sight_ray_mi.setDirection(0, -1, 0)
        self._sight_ray_mi = CollisionSegment()
        self._sight_ray_mi.setPointA(0, -1, 1)
        self._sight_ray_mi.setPointB(0,-3 * settings.GLOBAL_SCALE, 1)
        self._sight_coll_mi = CollisionNode('collision-sight-mi')
        self._sight_coll_mi.addSolid(self._sight_ray_mi)
        self._sight_coll_mi.setFromCollideMask(BitMask32.bit(5))
        self._sight_coll_mi.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_mi_path = self._model.attachNewNode(self._sight_coll_mi)
        #self._sight_coll_mi_path.show()
        self._coll_trav.addCollider(self._sight_coll_mi_path, self._sight_handler_mi)
        # Sight collision (left)
        self._sight_handler_le = CollisionHandlerQueue()
        #self._sight_ray_le = CollisionRay()
        #self._sight_ray_le.setOrigin(1, 0, 0)
        #self._sight_ray_le.setDirection(-.1, -1, 0)
        self._sight_ray_le = CollisionSegment()
        self._sight_ray_le.setPointA(0, -1, 1)
        self._sight_ray_le.setPointB(-1 * settings.GLOBAL_SCALE,-3 * settings.GLOBAL_SCALE, 1)
        self._sight_coll_le = CollisionNode('collision-sight-le')
        self._sight_coll_le.addSolid(self._sight_ray_le)
        self._sight_coll_le.setFromCollideMask(BitMask32.bit(5))
        self._sight_coll_le.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_le_path = self._model.attachNewNode(self._sight_coll_le)
        #self._sight_coll_le_path.show()
        self._coll_trav.addCollider(self._sight_coll_le_path, self._sight_handler_le)
        # Sight collision (right)
        self._sight_handler_ri = CollisionHandlerQueue()
        #self._sight_ray_ri = CollisionRay()
        #self._sight_ray_ri.setOrigin(1, 0, 0)
        #self._sight_ray_ri.setDirection(.1, -1, 0)
        self._sight_ray_ri = CollisionSegment()
        self._sight_ray_ri.setPointA(0, -1, 1)
        self._sight_ray_ri.setPointB(1 * settings.GLOBAL_SCALE,-3 * settings.GLOBAL_SCALE, 1)
        self._sight_coll_ri = CollisionNode('collision-sight-ri')
        self._sight_coll_ri.addSolid(self._sight_ray_ri)
        self._sight_coll_ri.setFromCollideMask(BitMask32.bit(5))
        self._sight_coll_ri.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_ri_path = self._model.attachNewNode(self._sight_coll_ri)
        #self._sight_coll_ri_path.show()
        self._coll_trav.addCollider(self._sight_coll_ri_path, self._sight_handler_ri)
        #Wall collision
        self._wall_handler = CollisionHandlerQueue()
        self._wall_ray = CollisionSphere(0,0,0,2)
        self._wall_coll = CollisionNode('collision-wall')
        self._wall_coll.addSolid(self._wall_ray)
        self._wall_coll.setFromCollideMask(BitMask32.bit(0))
        self._wall_coll.setIntoCollideMask(BitMask32.allOff())
        self._wall_coll_path = self._model.attachNewNode(self._wall_coll)
        #self._wall_coll_path.show()
        self._coll_trav.addCollider(self._wall_coll_path, self._wall_handler)

    def _setup_tasks(self):
        self._prev_time = 0
        taskMgr.add(self._move, "task-enemy-move")
        
    def _read_points(self,file_loc):
        f=open(file_loc)
        for line in f:
            if line!="\n":
                string.replace(line,' ','')
                line_arr=line.split(',')
                for i in range(0, len(line_arr)):
                    line_arr[i]=int(line_arr[i])
                self._points.append(line_arr)

    def _move(self, task):
        if self._is_moving==False:
            self._is_moving=True
            self._model.loop('enemove')
        if self.dead==False:
            et = task.time - self._prev_time
            rotation_rate = 100
            walk_rate = self._walk_rate

            # Get current values
            rotation = self._model.getH()
            pos_x = self._model.getX()
            pos_y = self._model.getY()
            pos = self._model.getPos()

            self._coll_trav.traverse(render)

            self._sight_handler_mi.sortEntries()
            self._sight_handler_ri.sortEntries()
            self._sight_handler_le.sortEntries()
            entries_wall = []
        
            for i in range(self._wall_handler.getNumEntries()):
                entries_wall.append(self._wall_handler.getEntry(i))

            if not self.is_valid(entries_wall):
                rotation += et * rotation_rate * random.randint(-1,1)
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad) * 10
                dy = et * walk_rate * -math.cos(rotation_rad) * 15
                pos_x -= dx
                pos_y -= dy
            elif self._sight_handler_mi.getNumEntries() and self._sight_handler_mi.getEntry(0).getIntoNode().getName() == 'collision-player-sphere' and \
                not self._is_cat:                                
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_ri.getNumEntries() and self._sight_handler_ri.getEntry(0).getIntoNode().getName() == 'collision-player-sphere' and \
                not self._is_cat:
                rotation += et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_le.getNumEntries() and self._sight_handler_le.getEntry(0).getIntoNode().getName() == 'collision-player-sphere' and \
                not self._is_cat:
                rotation -= et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            #Point to point movement will go here
            elif self._sight_handler_mi.getNumEntries() and self._sight_handler_mi.getEntry(0).getIntoNode().getName() == self._tag:
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_ri.getNumEntries() and self._sight_handler_ri.getEntry(0).getIntoNode().getName() == self._tag:
                rotation += et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_le.getNumEntries() and self._sight_handler_le.getEntry(0).getIntoNode().getName() == self._tag:
                rotation -= et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            else:
                rotation += et * rotation_rate

            # Save back to the model
            self._model.setH(rotation)
            
            self._model.setX(pos_x)
            self._model.setY(pos_y)
            self.pos = self._model.getPos()

            pos_z = self._model.getZ()
            entries = []
            
            for i in range(self._ground_handler.getNumEntries()):
                entries.append(self._ground_handler.getEntry(i))

            entries.sort(lambda x, y: cmp(y.getSurfacePoint(render).getZ(),
                                          x.getSurfacePoint(render).getZ()))
            
            if entries:
                is_valid = lambda x: x and x[0].getIntoNode().getName().find('ground1') != -1
                if entries[0].getSurfacePoint(render).getZ() < self._model.getZ():
                    self.gravity = 1
                if self.gravity == 1:
                    if entries[0].getSurfacePoint(render).getZ() >= self._model.getZ():
                        self.gravity=0
                    else:
                        self._model.setZ(pos_z - .5)
                elif is_valid(entries):
                    z = entries[0].getSurfacePoint(render).getZ()
                    if abs(z - self._model.getZ()) > 5:
                        self._model.setPos(pos)
                    else:
                        self._model.setZ(z)
                else:
                    self._model.setPos(self.pos)
            else:
                self._model.setPos(self.pos)

            self._prev_time = task.time

            return Task.cont
               
    def is_valid(self, entries):
        for x in entries:
            if x.getIntoNode().getName()!='ground1':
                return False
        return True
