import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

import math
import os

def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), font=loader.loadFont(os.path.join("fonts", "arial.ttf")),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

class Player(DirectObject):
    def __init__(self):
        self._keymap = {
                'forward' : 0,
                'reverse' : 0,
                'right'   : 0,
                'left'    : 0,
                'jump'    : 0,
        }
        self._dir = 0
        self._coll_dist = 10
        self._coll_dist_h = 3
        self._scale = .5
        self._load_models()
        self._load_sounds()
        self._load_lights()
        self._setup_actions()
        self._setup_tasks()
        self._setup_collisions()
        self.gravity = 0
        self.health = 100
        self.font = loader.loadFont(os.path.join("fonts", "arial.ttf"))
        self.bk_text= "Health   "
        self.textObject = OnscreenText(text=self.bk_text+str(self.health), font=self.font, pos = (-1, -.95),
                              scale=0.1, fg=(1, 1, 1, 1),
                              mayChange=1)
        self.inst1 = addInstructions(0.95, str(self._model.getPos()))

        
        self.win = False
    def _load_models(self):
        self._model = Actor("models/sdog")
        self._model.reparentTo(render)
        self._model.setPos(0, 0, 5)
        self._model.setScale(1)

    def _load_sounds(self):
        pass
        #self._sound_snowmobile = loader.loadSfx(os.path.join("sounds", "snowmobile-running.mp3"))

    def _load_lights(self):
        pass

    def _setup_actions(self):
        self.accept("arrow_up", self._set_key, ["forward", 1])
        self.accept("arrow_up-up", self._set_key, ["forward", 0])
        self.accept("arrow_down", self._set_key, ["reverse", 1])
        self.accept("arrow_down-up", self._set_key, ["reverse", 0])
        self.accept("arrow_left", self._set_key, ["left", 1])
        self.accept("arrow_left-up", self._set_key, ["left", 0])
        self.accept("arrow_right", self._set_key, ["right", 1])
        self.accept("arrow_right-up", self._set_key, ["right", 0])
        self.accept("w", self._set_key, ["forward", 1])
        self.accept("w-up", self._set_key, ["forward", 0])
        self.accept("s", self._set_key, ["reverse", 1])
        self.accept("s-up", self._set_key, ["reverse", 0])
        self.accept("a", self._set_key, ["left", 1])
        self.accept("a-up", self._set_key, ["left", 0])
        self.accept("d", self._set_key, ["right", 1])
        self.accept("d-up", self._set_key, ["right", 0])

        self.accept('space',self._set_key, ["jump", 1])
        self.accept('space-up', self._set_key, ["jump", 0])


    def _setup_tasks(self):
        self._prev_move_time = 0
        taskMgr.add(self._task_move, "player-task-move")
        taskMgr.add(self._update_camera, "update-camera")

    def _setup_collisions(self):
        self._coll_trav = CollisionTraverser()
        # Front collision
        self._gnd_handler_front = CollisionHandlerQueue()
        self._gnd_ray_front = CollisionRay()
        self._gnd_ray_front.setOrigin(0, self._coll_dist, 20)
        self._gnd_ray_front.setDirection(0, 0, -1)
        self._gnd_coll_front = CollisionNode('collision-ground-front')
        self._gnd_coll_front.addSolid(self._gnd_ray_front)
        self._gnd_coll_front.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_front.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_front = self._model.attachNewNode(self._gnd_coll_front)
        self._gnd_coll_path_front.show()
        self._coll_trav.addCollider(self._gnd_coll_path_front, self._gnd_handler_front)
        # Back collision
        self._gnd_handler_back = CollisionHandlerQueue()
        self._gnd_ray_back = CollisionRay()
        self._gnd_ray_back.setOrigin(0, -self._coll_dist, 20)
        self._gnd_ray_back.setDirection(0, 0, -1)
        self._gnd_coll_back = CollisionNode('collision-ground-back')
        self._gnd_coll_back.addSolid(self._gnd_ray_back)
        self._gnd_coll_back.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_back.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_back = self._model.attachNewNode(self._gnd_coll_back)
        self._gnd_coll_path_back.show()
        self._coll_trav.addCollider(self._gnd_coll_path_back, self._gnd_handler_back)
        # Left collision
        self._gnd_handler_left = CollisionHandlerQueue()
        self._gnd_ray_left = CollisionRay()
        self._gnd_ray_left.setOrigin(-self._coll_dist_h, 0, 20)
        self._gnd_ray_left.setDirection(0, 0, -1)
        self._gnd_coll_left = CollisionNode('collision-ground-left')
        self._gnd_coll_left.addSolid(self._gnd_ray_left)
        self._gnd_coll_left.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_left.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_left = self._model.attachNewNode(self._gnd_coll_left)
        self._gnd_coll_path_left.show()
        self._coll_trav.addCollider(self._gnd_coll_path_left, self._gnd_handler_left)
        # Right collision
        self._gnd_handler_right = CollisionHandlerQueue()
        self._gnd_ray_right = CollisionRay()
        self._gnd_ray_right.setOrigin(self._coll_dist_h, 0, 20)
        self._gnd_ray_right.setDirection(0, 0, -1)
        self._gnd_coll_right = CollisionNode('collision-ground-right')
        self._gnd_coll_right.addSolid(self._gnd_ray_right)
        self._gnd_coll_right.setFromCollideMask(BitMask32.bit(0))
        self._gnd_coll_right.setIntoCollideMask(BitMask32.allOff())
        self._gnd_coll_path_right = self._model.attachNewNode(self._gnd_coll_right)
        self._gnd_coll_path_right.show()
        self._coll_trav.addCollider(self._gnd_coll_path_right, self._gnd_handler_right)
        # Enemy sight target
        self._sphere_handler = CollisionHandlerQueue()
        self._sphere = CollisionSphere(0, 0, 0, 4)
        self._coll_sphere = CollisionNode('collision-player-sphere')
        self._coll_sphere.addSolid(self._sphere)
        self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
        self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
        self._coll_sphere_path = self._model.attachNewNode(self._coll_sphere)
        self._coll_sphere_path.show()
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

    def _set_key(self, key, value):
        self._keymap[key] = value

    def _update_camera(self, task):
        camera_h = base.camera.getH()
        camera_p = base.camera.getP()
        base.camera.lookAt(self._model)
        player_h = base.camera.getH()
        player_p = base.camera.getP()

        if player_h > camera_h:
            dest_h = min(camera_h+.5, player_h)
        else:
            dest_h = max(camera_h-.5, player_h)

        if player_p > camera_p:
            dest_p = min(camera_p+.5, player_p)
        else:
            dest_p = max(camera_p-.5, player_p)

        base.camera.setP(dest_p)
        base.camera.setH(dest_h)

        return Task.cont

    def _task_move(self, task):
        pos_z = self._model.getZ()

        for i in range(self._inner_sphere_handler.getNumEntries()):
            if self._inner_sphere_handler.getEntry(i).getIntoNode().getName()=='collision-with-player':
                self.health -= .5
        et = task.time - self._prev_move_time
        rotation_rate = 300
        walk_rate = 5
        # Get current values
        rotation = self._model.getH()
        pos_x = self._model.getX()
        pos_y = self._model.getY()
        pos = self._model.getPos()
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
      
        if self._keymap['jump']:
            pos_z += self._keymap['jump'] * 2
            self.gravity=1

        #if self._sound_snowmobile.status() == 1:
        #    if self._keymap['forward'] == 1 or self._keymap['reverse'] == 1 or self._keymap['left'] == 1 or self._keymap['right'] == 1:
        #        self._sound_snowmobile.play()
        #        self._sound_snowmobile.setLoop(True)
        #elif self._sound_snowmobile.status() == 2:
        #    if self._keymap['forward'] == 0 and self._keymap['reverse'] == 0 and self._keymap['left'] == 0 and self._keymap['right'] == 0:
        #        self._sound_snowmobile.stop()


        # Save back to the model
        self._model.setH(rotation)
        self._model.setX(pos_x)
        self._model.setY(pos_y)

        self._coll_trav.traverse(render)

        entries_front = []
        entries_back = []
        entries_left = []
        entries_right = []
        for i in range(self._gnd_handler_front.getNumEntries()):
            entries_front.append(self._gnd_handler_front.getEntry(i))
        for i in range(self._gnd_handler_back.getNumEntries()):
            entries_back.append(self._gnd_handler_back.getEntry(i))
        for i in range(self._gnd_handler_left.getNumEntries()):
            entries_left.append(self._gnd_handler_left.getEntry(i))
        for i in range(self._gnd_handler_right.getNumEntries()):
            entries_right.append(self._gnd_handler_right.getEntry(i))
        entries_all = entries_front + entries_back + entries_left + entries_right
        srt = lambda x, y: cmp(y.getSurfacePoint(render).getZ(),
                               x.getSurfacePoint(render).getZ())
        entries_front.sort(srt)
        entries_back.sort(srt)
        entries_left.sort(srt)
        entries_right.sort(srt)
        if entries_all:
            is_valid = lambda x: x and x[0].getIntoNode().getName().find('ground1') != -1
            if self.gravity == 1:
                self._model.setZ(pos_z)
                if entries_front[0].getSurfacePoint(render).getZ() == self._model.getZ():
                    self.gravity=0
                else:
                    self._model.setZ(pos_z-1)
            elif is_valid(entries_front) and is_valid(entries_back) and is_valid(entries_left) and is_valid(entries_right):
                f = entries_front[0].getSurfacePoint(render).getZ()
                b = entries_back[0].getSurfacePoint(render).getZ()
                l = entries_left[0].getSurfacePoint(render).getZ()
                r = entries_right[0].getSurfacePoint(render).getZ()
                z = (f + b) / 2
                if abs(z - self._model.getZ()) > 5:
                    self._model.setPos(pos)
                else:
                    self._model.setZ(z)
                    self._model.setP(rad2Deg(math.atan2(f - z, self._coll_dist * self._scale)))
                    self._model.setR(rad2Deg(math.atan2(l - z, self._coll_dist_h * self._scale)))
            else:
                self._model.setPos(pos)

        self._prev_move_time = task.time
        #Commented out some code due to panda3d assertion error
        #http://www.panda3d.org/phpbb2/viewtopic.php?p=38667
        if self.health >= 0:
            pass
            #self.textObject.setText(self.bk_text+str(self.health))
        if self.health <= 0 and self.win == False:
            pass
        """
             c = OnscreenImage(parent=render2d, image=os.path.join("models", "titlescreen.png"))
             lose = OnscreenText(text="You Lose!", font=self.font, pos = (0, 0.7),
                              scale=0.2, fg=(1, 1, 1, 1),
                              mayChange=0)
        """
        self.inst1.destroy()
        self.inst1 = addInstructions(0.95, str(self._model.getPos()))

        return Task.cont
    
