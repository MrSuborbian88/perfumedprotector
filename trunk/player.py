import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from pandac.PandaModules import BaseParticleEmitter,BaseParticleRenderer
from pandac.PandaModules import PointParticleFactory,SpriteParticleRenderer

import settings
import math
import os
import world

def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), font=loader.loadFont(os.path.join("fonts", "arial.ttf")),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

class Player(DirectObject):
    def __init__(self, dogSelection):
        self.playing_dead = False
        self._keymap = {
                'forward' : 0,
                'reverse' : 0,
                'right'   : 0,
                'left'    : 0,
                'jump'    : 0,
                'bark'    : 0,
        }
        self._dir = 0
        self.dogSelection = dogSelection
        if self.dogSelection == 2:
            self._coll_dist = 4
            self._coll_dist_h = 1.5
        else:
            self._coll_dist = 6
            self._coll_dist_h = 3
        self._scale = .5 * settings.GLOBAL_SCALE
        self._load_models()
        self._load_sounds()
        self._load_lights()
        self._setup_actions()
        self._setup_tasks()
        self._setup_collisions()
        self.gravity = 0
        self.jumping = 15
        self.falling = 0
        self.package = False
        self.jumpingCurrently = False
        self.chase = False
        self.chasetimer = settings.PLAYER_CHASE_LENGTH
        self.inst1 = addInstructions(0.95, str(self._model.getPos()))
        
        self.win = False
    def _load_models(self):
        if self.dogSelection == 2:
            self._model = Actor("models/sdog.egg", {"walking":"models/sdoganim.egg"})
            #self._model2 = Actor("models/sdogb.egg", {"walking":"models/sdoganimb.egg"})
        else:
            self._model = Actor("models/bdog", {"walking":"models/bdoganim.egg"})
            #self._model2 = Actor("models/bdogb", {"walking":"models/bdoganimb.egg"})
        self.animControl =self._model.getAnimControl('walking')
        self.currentFrame = self.animControl.getFrame()
        self._model.reparentTo(render)
        self._model.setScale(.5 * settings.GLOBAL_SCALE)
        self._model.setPos(550, 0, 5)
        self._model.setH(-90)
        self.p = ParticleEffect()

    def _load_sounds(self):
        self.sound_bark = loader.loadSfx(os.path.join("sound files", "Dog Barking.mp3"))
        self.sound_dog_footsteps = loader.loadSfx(os.path.join("sound files", "Dog Footsteps.mp3"))

    def _load_lights(self):
        pass

    def _setup_actions(self):
        """
        self.accept("arrow_up", self._set_key, ["reverse", 1])
        self.accept("arrow_up-up", self._set_key, ["reverse", 0])
        self.accept("arrow_down", self._set_key, ["forward", 1])
        self.accept("arrow_down-up", self._set_key, ["forward", 0])
        self.accept("arrow_left", self._set_key, ["left", 1])
        self.accept("arrow_left-up", self._set_key, ["left", 0])
        self.accept("arrow_right", self._set_key, ["right", 1])
        self.accept("arrow_right-up", self._set_key, ["right", 0])
        """
        self.accept("w", self._set_key, ["reverse", 1])
        self.accept("w-up", self._set_key, ["reverse", 0])
        self.accept("s", self._set_key, ["forward", 1])
        self.accept("s-up", self._set_key, ["forward", 0])
        self.accept("a", self._set_key, ["left", 1])
        self.accept("a-up", self._set_key, ["left", 0])
        self.accept("d", self._set_key, ["right", 1])
        self.accept("d-up", self._set_key, ["right", 0])
        self.accept("e", self._set_key, ["bark", 1])
        self.accept('space',self._set_key, ["jump", 1])
        self.accept('space-up', self._set_key, ["jump", 0])
        self.accept('f', self.play_dead)

    def _setup_tasks(self):
        self._prev_move_time = 0
        taskMgr.add(self._task_move, "player-task-move")
        taskMgr.add(self._update_camera, "update-camera")

    def _setup_collisions(self):
        self._coll_trav = CollisionTraverser()
        # Front collision
        self._gnd_handler_front = CollisionHandlerQueue()
        self._gnd_ray_front = CollisionRay()
        self._gnd_ray_front.setOrigin(0, self._coll_dist, 1)
        self._gnd_ray_front.setDirection(0, 0, -1)
        self._gnd_coll_front = CollisionNode('collision-ground-front')
        self._gnd_coll_front.addSolid(self._gnd_ray_front)
        self._gnd_coll_front.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_front.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_front = self._model.attachNewNode(self._gnd_coll_front)
        #self._gnd_coll_path_front.show()
        self._coll_trav.addCollider(self._gnd_coll_path_front, self._gnd_handler_front)
         # Front-left collision
        self._gnd_handler_front_left = CollisionHandlerQueue()
        self._gnd_ray_front_left = CollisionRay()
        self._gnd_ray_front_left.setOrigin(-self._coll_dist_h, self._coll_dist/2, 1)
        self._gnd_ray_front_left.setDirection(0, 0, -1)
        self._gnd_coll_front_left = CollisionNode('collision-ground-front-left')
        self._gnd_coll_front_left.addSolid(self._gnd_ray_front_left)
        self._gnd_coll_front_left.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_front_left.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_front_left = self._model.attachNewNode(self._gnd_coll_front_left)
        #self._gnd_coll_path_front_left.show()
        self._coll_trav.addCollider(self._gnd_coll_path_front_left, self._gnd_handler_front_left)
         # Front-right collision
        self._gnd_handler_front_right = CollisionHandlerQueue()
        self._gnd_ray_front_right = CollisionRay()
        self._gnd_ray_front_right.setOrigin(self._coll_dist_h, self._coll_dist/2, 1)
        self._gnd_ray_front_right.setDirection(0, 0, -1)
        self._gnd_coll_front_right = CollisionNode('collision-ground-front-right')
        self._gnd_coll_front_right.addSolid(self._gnd_ray_front_right)
        self._gnd_coll_front_right.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_front_right.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_front_right = self._model.attachNewNode(self._gnd_coll_front_right)
        #self._gnd_coll_path_front_right.show()
        self._coll_trav.addCollider(self._gnd_coll_path_front_right, self._gnd_handler_front_right)
        # Back collision
        self._gnd_handler_back = CollisionHandlerQueue()
        self._gnd_ray_back = CollisionRay()
        self._gnd_ray_back.setOrigin(0, -self._coll_dist, 1)
        self._gnd_ray_back.setDirection(0, 0, -1)
        self._gnd_coll_back = CollisionNode('collision-ground-back')
        self._gnd_coll_back.addSolid(self._gnd_ray_back)
        self._gnd_coll_back.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_back.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_back = self._model.attachNewNode(self._gnd_coll_back)
        #self._gnd_coll_path_back.show()
        self._coll_trav.addCollider(self._gnd_coll_path_back, self._gnd_handler_back)
        # Back-left collision
        self._gnd_handler_back_left = CollisionHandlerQueue()
        self._gnd_ray_back_left = CollisionRay()
        self._gnd_ray_back_left.setOrigin(-self._coll_dist_h, -self._coll_dist/2, 1)
        self._gnd_ray_back_left.setDirection(0, 0, -1)
        self._gnd_coll_back_left = CollisionNode('collision-ground-back-left')
        self._gnd_coll_back_left.addSolid(self._gnd_ray_back_left)
        self._gnd_coll_back_left.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_back_left.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_back_left = self._model.attachNewNode(self._gnd_coll_back_left)
        #self._gnd_coll_path_back_left.show()
        self._coll_trav.addCollider(self._gnd_coll_path_back_left, self._gnd_handler_back_left)
        # Back-right collision
        self._gnd_handler_back_right = CollisionHandlerQueue()
        self._gnd_ray_back_right = CollisionRay()
        self._gnd_ray_back_right.setOrigin(self._coll_dist_h, -self._coll_dist/2, 1)
        self._gnd_ray_back_right.setDirection(0, 0, -1)
        self._gnd_coll_back_right = CollisionNode('collision-ground-back-right')
        self._gnd_coll_back_right.addSolid(self._gnd_ray_back_right)
        self._gnd_coll_back_right.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_back_right.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_back_right = self._model.attachNewNode(self._gnd_coll_back_right)
        #self._gnd_coll_path_back_right.show()
        self._coll_trav.addCollider(self._gnd_coll_path_back_right, self._gnd_handler_back_right)
        # Left collision
        self._gnd_handler_left = CollisionHandlerQueue()
        self._gnd_ray_left = CollisionRay()
        self._gnd_ray_left.setOrigin(-self._coll_dist_h, 0, 1)
        self._gnd_ray_left.setDirection(0, 0, -1)
        self._gnd_coll_left = CollisionNode('collision-ground-left')
        self._gnd_coll_left.addSolid(self._gnd_ray_left)
        self._gnd_coll_left.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_left.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_left = self._model.attachNewNode(self._gnd_coll_left)
        #self._gnd_coll_path_left.show()
        self._coll_trav.addCollider(self._gnd_coll_path_left, self._gnd_handler_left)
        # Right collision
        self._gnd_handler_right = CollisionHandlerQueue()
        self._gnd_ray_right = CollisionRay()
        self._gnd_ray_right.setOrigin(self._coll_dist_h, 0, 1)
        self._gnd_ray_right.setDirection(0, 0, -1)
        self._gnd_coll_right = CollisionNode('collision-ground-right')
        self._gnd_coll_right.addSolid(self._gnd_ray_right)
        self._gnd_coll_right.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_right.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_right = self._model.attachNewNode(self._gnd_coll_right)
        #self._gnd_coll_path_right.show()
        self._coll_trav.addCollider(self._gnd_coll_path_right, self._gnd_handler_right)
        
        #Wall collision
        self._wall_handler = CollisionHandlerQueue()
        self._wall_ray = CollisionSegment()
        self._wall_ray.setPointA(0, self._coll_dist, 2)
        self._wall_ray.setPointB(0, -self._coll_dist, 2)
        self._wall_coll = CollisionNode('collision-wall')
        self._wall_coll.addSolid(self._wall_ray)
        self._wall_coll.setFromCollideMask(BitMask32.bit(0))
        self._wall_coll.setIntoCollideMask(BitMask32.allOff())
        self._wall_coll_path = self._model.attachNewNode(self._wall_coll)
        #self._wall_coll_path.show()
        self._coll_trav.addCollider(self._wall_coll_path, self._wall_handler)
        
        # Enemy sight target
        self._sphere_handler = CollisionHandlerQueue()
        self._sphere = CollisionSphere(0, 0, 0, 4)
        self._coll_sphere = CollisionNode('collision-player-sphere')
        self._coll_sphere.addSolid(self._sphere)
        self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
        self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
        self._coll_sphere_path = self._model.attachNewNode(self._coll_sphere)
        #self._coll_sphere_path.show()
        self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        # Inner sphere collision
        self._inner_sphere_handler = CollisionHandlerQueue()
        self._inner_sphere = CollisionSphere(0, 0, 0, 4)
        self._coll_inner_sphere = CollisionNode('collision-player-sphere-inner')
        self._coll_inner_sphere.addSolid(self._inner_sphere)
        self._coll_inner_sphere.setFromCollideMask(BitMask32.bit(7))
        self._coll_inner_sphere.setIntoCollideMask(BitMask32.bit(7))
        self._coll_inner_sphere_path = self._model.attachNewNode(self._coll_inner_sphere)
        #self._coll_inner_sphere_path.show()
        self._coll_trav.addCollider(self._coll_inner_sphere_path, self._inner_sphere_handler)
        # Sight collision (Mid)
        self._sight_handler_mi = CollisionHandlerQueue()
        self._sight_ray_mi = CollisionRay()
        self._sight_ray_mi.setOrigin(1, 0, 1)
        self._sight_ray_mi.setDirection(0, -1, 0)
        self._sight_coll_mi = CollisionNode('collision-sight-mi')
        self._sight_coll_mi.addSolid(self._sight_ray_mi)
        self._sight_coll_mi.setFromCollideMask(BitMask32.bit(6))
        self._sight_coll_mi.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_mi_path = self._model.attachNewNode(self._sight_coll_mi)
        #self._sight_coll_mi_path.show()
        self._coll_trav.addCollider(self._sight_coll_mi_path, self._sight_handler_mi)
        # Sight collision (left)
        self._sight_handler_le = CollisionHandlerQueue()
        self._sight_ray_le = CollisionRay()
        self._sight_ray_le.setOrigin(1, 0, 1)
        self._sight_ray_le.setDirection(-.1, -1, 0)
        self._sight_coll_le = CollisionNode('collision-sight-le')
        self._sight_coll_le.addSolid(self._sight_ray_le)
        self._sight_coll_le.setFromCollideMask(BitMask32.bit(6))
        self._sight_coll_le.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_le_path = self._model.attachNewNode(self._sight_coll_le)
        #self._sight_coll_le_path.show()
        self._coll_trav.addCollider(self._sight_coll_le_path, self._sight_handler_le)
        # Sight collision (right)
        self._sight_handler_ri = CollisionHandlerQueue()
        self._sight_ray_ri = CollisionRay()
        self._sight_ray_ri.setOrigin(1, 0, 1)
        self._sight_ray_ri.setDirection(.1, -1, 0)
        self._sight_coll_ri = CollisionNode('collision-sight-ri')
        self._sight_coll_ri.addSolid(self._sight_ray_ri)
        self._sight_coll_ri.setFromCollideMask(BitMask32.bit(6))
        self._sight_coll_ri.setIntoCollideMask(BitMask32.allOff())
        self._sight_coll_ri_path = self._model.attachNewNode(self._sight_coll_ri)
        #self._sight_coll_ri_path.show()
        self._coll_trav.addCollider(self._sight_coll_ri_path, self._sight_handler_ri)

    def _set_key(self, key, value):
        self._keymap[key] = value

    def _update_camera(self, task):
        if self.playing_dead == False:
            camera_h = base.camera.getH()
            camera_p = base.camera.getP()
            base.camera.lookAt(self._model)
            target_h = base.camera.getH()
            target_p = base.camera.getP()

            if camera_h < -180:
                camera_h = (180 - (camera_h + 180))
            elif camera_h > 180:
                camera_h = (-180 + (camera_h - 180))

            if camera_h == target_h and camera_p == target_p:
                return Task.cont

            diff_h = camera_h-target_h
            diff_p = camera_p-target_p

            if abs(diff_h) > abs(diff_p):
                if diff_h==0:
                    p_p = 1
                    p_h = 0
                else:
                    p_p = abs(diff_p / diff_h)
                    p_h = 1
            else:
                if diff_p==0:
                    p_h = 1
                    p_p = 1
                else:
                    p_h = abs(diff_h / diff_p)
                    p_p = 1

            if camera_h == target_h:
                dest_h = target_h
                dest_p = target_p
            elif diff_h > 180 or (diff_h < 0 and diff_h > -180):
                dest_h = camera_h+(.5*p_h)
                if dest_h > target_h:
                    dest_h = target_h
            elif diff_h <= -180 or (diff_h > 0 and diff_h <= 180):
                dest_h = camera_h-(.5*p_h)
                if dest_h < target_h:
                    dest_h = target_h
            else:
                dest_h=target_h

            if target_p > camera_p:
                dest_p = min(camera_p+(.5*p_p), target_p)
            elif target_p < camera_p:
                dest_p = max(camera_p-(.5*p_p), target_p)
            else:
                dest_p=target_p

            base.camera.setP(dest_p)
            base.camera.setH(dest_h)
        return Task.cont
    def _switch_models(self):
        pos = self._model.getPos()
        rot = self._model.getH()
        p = self._model.getP()
        r = self._model.getR()
        self._model.cleanup()
        self._model.removeNode()
        if self.dogSelection == 2:
            self._model = Actor("models/sdogb.egg", {"walking":"models/sdoganimb.egg"})
        else:
            self._model = Actor("models/bdogb", {"walking":"models/bdoganimb.egg"})
        #self.animControl =self._model.getAnimControl('walking')
        self._model.reparentTo(render)
        self._model.setScale(.5 * settings.GLOBAL_SCALE)
        self._model.setPos(550, 0, 5)
        self._model.setH(-90)
        self.p = ParticleEffect()
        self._setup_collisions()
        self._model.setPos(pos)
        self._model.setH(rot)
        self._model.setP(p)
        self._model.setR(r)
        
    def _task_move(self, task):
        pos_z = self._model.getZ()
        for i in range(self._inner_sphere_handler.getNumEntries()):
            if self._inner_sphere_handler.getEntry(i).getIntoNode().getName()=='collision-with-player-cat':
                if self.chasetimer >= settings.PLAYER_CHASE_LENGTH:
                    self.chase = True
            elif self._inner_sphere_handler.getEntry(i).getIntoNode().getName()=='collision-with-player-dcatcher':
                print "Captured"
            elif self._inner_sphere_handler.getEntry(i).getIntoNode().getName()=='collision-package':
                self._switch_models()
                self.package = True

        if self.playing_dead or self._model.getR()>0:
            if self.playing_dead:
                if self._model.getR() < 90:
                    self._model.setR(self._model.getR()+10)
            else:
                if self._model.getR() > 0:
                    self._model.setR(self._model.getR()-10)
            self._prev_move_time = task.time
            return Task.cont

        et = task.time - self._prev_move_time
        rotation_rate = settings.PLAYER_ROTATION_RATE
        walk_rate = settings.PLAYER_WALK_RATE
        # Get current values
        rotation = self._model.getH()
        pos_x = self._model.getX()
        pos_y = self._model.getY()
        pos = self._model.getPos()
        
        if self.chase:
            self._inner_sphere_handler.sortEntries()
            if self._inner_sphere_handler.getNumEntries() and self._inner_sphere_handler.getEntry(0).getIntoNode().getName() == 'collision-enemy-sphere':
                    self._prev_move_time = task.time
                    return Task.cont

            self._sight_handler_mi.sortEntries()
            self._sight_handler_ri.sortEntries()
            self._sight_handler_le.sortEntries()
        
            if self._sight_handler_mi.getNumEntries() and self._sight_handler_mi.getEntry(0).getIntoNode().getName() == 'collision-chase-sphere':
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_ri.getNumEntries() and self._sight_handler_ri.getEntry(0).getIntoNode().getName() == 'collision-chase-sphere':
                rotation += et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            elif self._sight_handler_le.getNumEntries() and self._sight_handler_le.getEntry(0).getIntoNode().getName() == 'collision-chase-sphere':
                rotation -= et * rotation_rate
                rotation_rad = deg2Rad(rotation)
                dx = et * walk_rate * math.sin(rotation_rad)
                dy = et * walk_rate * -math.cos(rotation_rad)
                pos_x += dx
                pos_y += dy
            else:
                rotation += et * rotation_rate

            self._model.setH(rotation)
            self._model.setX(pos_x)
            self._model.setY(pos_y)

            self.chasetimer -= 1
            if self.chasetimer == 0:
                self.chase = False
            #self._prev_move_time = task.time

            #return Task.cont



        # Rotate the player
        dr = et * rotation_rate
        rotation += self._keymap['left'] * dr
        rotation -= self._keymap['right'] * dr
        # Move the player
        rotation_rad = deg2Rad(rotation)
        dx = et * walk_rate * -math.sin(rotation_rad)
        dy = et * walk_rate * math.cos(rotation_rad)
        pos_x += self._keymap['forward'] * dx
        pos_y += self._keymap['forward'] * dy
        pos_x -= self._keymap['reverse'] * dx
        pos_y -= self._keymap['reverse'] * dy

        if self._keymap['jump'] and not self.jumpingCurrently and self.dogSelection==2:
            self.jumpingCurrently=True

        if self.jumpingCurrently:
                temp=self.jump()
                if (temp+pos_z) < 190:
                    pos_z+=temp
                else:
                    self.jumping=0

        if self._keymap['bark'] and self.dogSelection == 1:
            self.sound_bark.play()
            self._keymap['bark'] = 0
            self.chase = False
            self.loadParticleConfig((42,-261,10))
        
        if self._keymap['forward'] == 1 or self._keymap['reverse'] == 1 or self._keymap['left'] == 1 or self._keymap['right'] == 1:
            if not self.animControl.isPlaying(): 
                self._model.loop('walking')
        else:
            self.currentFrame = self.animControl.getFrame()
            self._model.pose('walking', self.currentFrame)
        
        if self.sound_dog_footsteps.status() == 1:
            if self._keymap['forward'] == 1 or self._keymap['reverse'] == 1 or self._keymap['left'] == 1 or self._keymap['right'] == 1:
                self.sound_dog_footsteps.play()
                self.sound_dog_footsteps.setLoop(True)
        elif self.sound_dog_footsteps.status() == 2:
            if self._keymap['forward'] == 0 and self._keymap['reverse'] == 0 and self._keymap['left'] == 0 and self._keymap['right'] == 0:
                self.sound_dog_footsteps.stop()


        # Save back to the model
        self._model.setH(rotation)
        self._model.setX(pos_x)
        self._model.setY(pos_y)

        self._coll_trav.traverse(render)

        entries_wall = []
        entries_front = []
        entries_front_left = []
        entries_front_right = []
        entries_back = []
        entries_back_left = []
        entries_back_right = []
        entries_left = []
        entries_right = []

        for i in range(self._wall_handler.getNumEntries()):
            entries_wall.append(self._wall_handler.getEntry(i))
        for i in range(self._gnd_handler_front.getNumEntries()):
            entries_front.append(self._gnd_handler_front.getEntry(i))
        for i in range(self._gnd_handler_back.getNumEntries()):
            entries_back.append(self._gnd_handler_back.getEntry(i))
        for i in range(self._gnd_handler_left.getNumEntries()):
            entries_left.append(self._gnd_handler_left.getEntry(i))
        for i in range(self._gnd_handler_right.getNumEntries()):
            entries_right.append(self._gnd_handler_right.getEntry(i))
        for i in range(self._gnd_handler_front_left.getNumEntries()):
            entries_front_left.append(self._gnd_handler_front_left.getEntry(i))
        for i in range(self._gnd_handler_back_left.getNumEntries()):
            entries_back_left.append(self._gnd_handler_back_left.getEntry(i))
        for i in range(self._gnd_handler_front_right.getNumEntries()):
            entries_front_right.append(self._gnd_handler_front_right.getEntry(i))
        for i in range(self._gnd_handler_back_right.getNumEntries()):
            entries_back_right.append(self._gnd_handler_back_right.getEntry(i))

        entries_all = entries_front + entries_back + entries_left + entries_right + entries_front_right + entries_back_right + entries_front_left + entries_back_left
        srt = lambda x, y: cmp(y.getSurfacePoint(render).getZ(),
                               x.getSurfacePoint(render).getZ())
        entries_front.sort(srt)
        entries_back.sort(srt)
        entries_left.sort(srt)
        entries_right.sort(srt)
        entries_front_right.sort(srt)
        entries_front_left.sort(srt)
        entries_back_left.sort(srt)
        entries_back_right.sort(srt)
        entries_wall.sort(srt)

        if entries_all:
            if self.gravity == 1:
                self._model.setZ(pos_z)
                if entries_back:
                    if entries_back[0].getSurfacePoint(render).getZ()>self._model.getZ():
                        self._model.setZ(entries_back[0].getSurfacePoint(render).getZ())
                        self.gravity=0
                        self.jumpingCurrently=False
                        self.jumping=15
                        self.falling=0
                    if self.gravity == 1 and not self.jumpingCurrently:
                        pos_z+=self.fall()
                        self._model.setZ(pos_z)
                else:
                    if entries_front[0].getSurfacePoint(render).getZ()>self._model.getZ():
                        self._model.setZ(entries_front[0].getSurfacePoint(render).getZ())
                        self.gravity=0
                        self.jumpingCurrently=False
                        self.jumping=15
                        self.falling=0
                    if self.gravity == 1 and not self.jumpingCurrently:
                        pos_z+=self.fall()
                        self._model.setZ(pos_z)
            #elif self.is_valid(entries_front) and self.is_valid(entries_back) and self.is_valid(entries_left) and self.is_valid(entries_right) and self.is_valid(entries_front_right) and self.is_valid(entries_front_left) and self.is_valid(entries_back_left) and self.is_valid(entries_back_right):
            elif self.is_valid(entries_wall):
                if len(entries_front) > 0 and len(entries_back) > 0:
                    f = entries_front[0].getSurfacePoint(render).getZ()
                    b = entries_back[0].getSurfacePoint(render).getZ()
                    #l = entries_left[0].getSurfacePoint(render).getZ()
                    #r = entries_right[0].getSurfacePoint(render).getZ()
                    z = (f + b) / 2
                    if abs(z - self._model.getZ()) > 5:
                        self.gravity=1
                    else:
                        #self._model.setZ(z)
                        #self._model.setP(rad2Deg(math.atan2(f - z, self._coll_dist * self._scale)))
                        #self._model.setR(rad2Deg(math.atan2(l - z, self._coll_dist_h * self._scale)))
                        pass
            else:
                self._model.setPos(pos)


        if not self.chase and self.chasetimer < settings.PLAYER_CHASE_LENGTH:
            self.chasetimer += 1

        self._prev_move_time = task.time


        self.inst1.destroy()
        self.inst1 = addInstructions(0.95, str(self._model.getPos()))
            
        return Task.cont
    
    def is_valid(self, entries):
        #if len(entries) == 0:
         #return False
        for x in entries:
             if x.getIntoNode().getName()!='ground1':
                return False
        return True
    
    def jump(self):
        if self.jumping>0:
            self.gravity=1
            self.jumping-=.5
            return self.jumping*.5
        else:
            return self.fall()
    def fall(self):
            self.falling-=.5
            return self.falling*.5
    
    def loadParticleConfig(self, position):
        self.p.cleanup()
        self.p = ParticleEffect()
        self.p.loadConfig(os.path.join("models", "smokering.ptf"))   
        self.p.accelerate(.25) 
        self.p.setPos(position) 
        self.p.reparentTo(render) 
        self.p.setScale(10)  
        self.p.start()
        taskMgr.doMethodLater(5, self.cleanParticles, 'Stop Particles')
        
    def cleanParticles(self, random):
        self.p.softStop()

        
    def play_dead(self):
        self.playing_dead = not self.playing_dead
        if self.playing_dead:
            self._model.setR(self._model.getR()+10)
            self._model.setZ(self._model.getZ()+1)
        else:
            self._model.setR(self._model.getR()-10)
            self._model.setZ(self._model.getZ()-1)
