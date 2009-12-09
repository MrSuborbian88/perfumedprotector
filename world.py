import settings
import player
import cat
import dogcatcher
import sys
from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'window-title Doggy Delivery')
loadPrcFileData('', 'notify-level fatal')
import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject 
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.task import Task

GAME_STARTED = False
ROOM_OFFSETS = [(0,0,0),        #placeholder - no room 0
                (0,0,0),        #1
                (0,0,0),        #2
                (190,-486,0),   #3
                (388,565,0),    #4
                (0,0,0),        #placeholder - no room 5
                (1077,79,0),    #6 83
                (0,0,0),        #7
                (0,0,0),        #8
                (0,0,0),        #9
                (0,0,0),        #10
                (0,0,0),        #11
                (0,0,0),        #12
                (0,0,0),        #13
                (0,0,0),        #14
                (0,0,0),        #15
                (0,0,0),        #16
                (0,0,0),        #17
                (0,0,0)]        #18

ROOM_LOADS = [(0),              #placeholder - no room 0
              (1,2),            #1
              (1,2,3,4),        #2
              (2,3,6),          #3
              (2,4,6),          #4
              (0),              #placeholder - no room 5
              (3,4,6),          #6(3,4,6,7,9)
              (6,7,8),          #7
              (7,8,9,11,14),    #8
              (6,8,9,10),       #9
              (9,10,13),        #10
              (8,11,12,13,18),  #11
              (11,12,14,18),    #12
              (10,11,13,15,18), #13
              (8,12,14),        #14
              (13,15,16,18),    #15
              (15,16,18),       #16
              (16,17),          #17
              (11,12,13,15,18)] #18

class World(DirectObject):
    def __init__(self, dogSelection):
        base.disableMouse()
        render.setShaderAuto()
        self.dogSelection = dogSelection
        self.current_room = 2
        self.pan_tar = 1
        self._setup_models()
        self._preload_rooms()
        self._setup_room_collisions()
        self._setup_lights()
        self._setup_actions()
        self._setup_cam()
        self._load_rooms(2)

        taskMgr.doMethodLater(2, self.camera_pan, "cam_pan")

    def _setup_cam(self):
        base.camera.setPos(self.room2.find("**/camera_loc").getPos() + ROOM_OFFSETS[2])
        base.camera.lookAt(self.room2.find("**/camera_start_look").getPos() + ROOM_OFFSETS[2])

    def _setup_models(self):
        self.player = player.Player(self.dogSelection)
        base.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerEvent()
        self.cHandler.setInPattern("artifact_gotten") #artifact gotten?
        self.env = render.attachNewNode("env")
        self.rooms = []
        self.enemylist = []

    def _setup_lights(self):
        ambient = AmbientLight("light-ambient")
        ambient.setColor((.4, .4, .4, 1))
        ambient_path = render.attachNewNode(ambient)
        render.setLight(ambient_path)
        pointlight = PointLight("pointlight")
        pointlight.setColor(VBase4(0.2, 0.2, 0.2, 1))
        plnp = render.attachNewNode(pointlight)
        plnp.setPos(0, 0, 5)
        render.setLight(plnp)

    def _setup_actions(self):
        self.accept("escape", sys.exit)

    def _spawn_enemy(self,pos,file_loc):
        self._coll_trav = CollisionTraverser()
        enemy = dogcatcher.DogCatcher(pos,file_loc)
        for p in enemy._points:
                self._sphere_handler = CollisionHandlerQueue()
                #self._sphere = CollisionSphere(p[0]/settings.ENV_SCALE, p[1]/settings.ENV_SCALE, p[2], 2 * settings.ENV_SCALE)
                self._sphere = CollisionSphere(p[0], p[1], p[2],10 * settings.ENV_SCALE)
                self._coll_sphere = CollisionNode('collision-point-sphere')
                self._coll_sphere.addSolid(self._sphere)
                self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
                self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
                self._coll_sphere_path = self.env.attachNewNode(self._coll_sphere)
                self._coll_sphere_path.show()
                self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        self.enemylist.append(enemy)
        
    def _spawn_cat(self,pos,file_loc):
        self._coll_trav = CollisionTraverser()
        enemy = cat.Cat(pos,file_loc)
        for p in enemy._points:
                self._sphere_handler = CollisionHandlerQueue()
                #self._sphere = CollisionSphere(p[0]/settings.ENV_SCALE, p[1]/settings.ENV_SCALE, p[2], 2 * settings.ENV_SCALE)
                self._sphere = CollisionSphere(p[0], p[1], p[2],10 * settings.ENV_SCALE)
                self._coll_sphere = CollisionNode('collision-point-sphere')
                self._coll_sphere.addSolid(self._sphere)
                self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
                self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
                self._coll_sphere_path = self.env.attachNewNode(self._coll_sphere)
                self._coll_sphere_path.show()
                self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        self.enemylist.append(enemy)
    def _setup_room_collisions(self):
        pass

    def _change_room(self, num):
        self.current_room = num
        self.player.current_room = num
        #change cameras
        _load_rooms(num)

    def _load_rooms(self, current):
        #self.room1.detachNode()
        self.room2.detachNode()
        self.room3.detachNode()
        self.room4.detachNode()
        self.room6.detachNode()
        """self.room7.detachNode()
        self.room8.detachNode()
        self.room9.detachNode()
        self.room10.detachNode()
        self.room11.detachNode()
        self.room12.detachNode()
        self.room13.detachNode()
        self.room14.detachNode()
        self.room15.detachNode()
        self.room16.detachNode()
        self.room17.detachNode()
        self.room18.detachNode()
        """
        for r in ROOM_LOADS[current]:
            print "loading room %d" % r
            self.rooms[r].reparentTo(self.env)

    def _preload_rooms(self):
        self.rooms.append(NodePath())
        """self.room1 = loader.loadModel("models/room1")
        self.room1.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room1.setPos(ROOM_OFFSETS[1][0], ROOM_OFFSETS[1][1], ROOM_OFFSETS[1][2])
        self.rooms.append(self.room1)
        """
        self.room1 = loader.loadModel("models/room2")
        self.room1.setScale(.0001)
        self.room1.setPos(-2000,-2000,-2000)
        self.rooms.append(self.room1)

        self.room2 = loader.loadModel("models/room2")
        self.room2.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room2.setPos(ROOM_OFFSETS[2][0], ROOM_OFFSETS[2][1], ROOM_OFFSETS[2][2])
        self.rooms.append(self.room2)
        self._spawn_enemy((80,123,40), "data/room2.txt")
        self._spawn_cat((40,100,40), "data/room2.txt")

        #load room1 and room2 to start
        #self.room1.reparentTo(self.env)
        self.room2.reparentTo(self.env)

        self.room3 = loader.loadModel("models/room3")
        self.room3.setH(-90)
        self.room3.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room3.setPos(ROOM_OFFSETS[3][0], ROOM_OFFSETS[3][1], ROOM_OFFSETS[3][2])
        self.rooms.append(self.room3)

        self.room4 = loader.loadModel("models/room4")
        self.room4.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room4.setPos(ROOM_OFFSETS[4][0], ROOM_OFFSETS[4][1], ROOM_OFFSETS[4][2])
        self.rooms.append(self.room4)

        self.room5 = loader.loadModel("models/room2")
        self.room5.setScale(.0001)
        self.rooms.append(self.room5)

        self.room6 = loader.loadModel("models/room6")
        self.room6.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room6.setPos(ROOM_OFFSETS[6][0], ROOM_OFFSETS[6][1], ROOM_OFFSETS[6][2])
        self.rooms.append(self.room6)

        """self.room7 = loader.loadModel("models/room7")
        self.room7.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room7.setPos(ROOM_OFFSETS[7][0], ROOM_OFFSETS[7][1], ROOM_OFFSETS[7][2])
        self.rooms.append(self.room7)

        self.room8 = loader.loadModel("models/room8")
        self.room8.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room8.setPos(ROOM_OFFSETS[8][0], ROOM_OFFSETS[8][1], ROOM_OFFSETS[8][2])
        self.rooms.append(self.room8)

        self.room9 = loader.loadModel("models/room9")
        self.room9.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room9.setPos(ROOM_OFFSETS[9][0], ROOM_OFFSETS[9][1], ROOM_OFFSETS[9][2])
        self.rooms.append(self.room9)

        self.room10 = loader.loadModel("models/room10")
        self.room10.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room10.setPos(ROOM_OFFSETS[10][0], ROOM_OFFSETS[10][1], ROOM_OFFSETS[10][2])
        self.rooms.append(self.room10)

        self.room11 = loader.loadModel("models/room11")
        self.room11.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room11.setPos(ROOM_OFFSETS[11][0], ROOM_OFFSETS[11][1], ROOM_OFFSETS[11][2])
        self.rooms.append(self.room11)

        self.room12 = loader.loadModel("models/room12")
        self.room12.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room12.setPos(ROOM_OFFSETS[12][0], ROOM_OFFSETS[12][1], ROOM_OFFSETS[12][2])
        self.rooms.append(self.room12)

        self.room13 = loader.loadModel("models/room13")
        self.room13.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room13.setPos(ROOM_OFFSETS[13][0], ROOM_OFFSETS[13][1], ROOM_OFFSETS[13][2])
        self.rooms.append(self.room13)
        """

    def camera_pan(self, task):
        if self.player.playing_dead:
            camera_h = base.camera.getH()
            camera_p = base.camera.getP()

            if self.pan_tar == 1:
                base.camera.lookAt(self.rooms[self.current_room].find("**/camera_pan_1").getPos() + ROOM_OFFSETS[self.current_room])
            else:
                self.pan_tar = 0
                base.camera.lookAt(self.rooms[self.current_room].find("**/camera_pan_2").getPos() + ROOM_OFFSETS[self.current_room])

            target_h = base.camera.getH()
            target_p = base.camera.getP()

            diff_h = camera_h-target_h
            diff_p = camera_p-target_p

            if abs(diff_h) > abs(diff_p):
                if diff_h==0:
                    p_p = 1
                    p_h = 0
                else:
                    p_p = abs(float(diff_p) / float(diff_h))
                    p_h = 1
            else:
                if diff_p==0:
                    p_h = 1
                    p_p = 1
                else:
                    p_h = abs(float(diff_h) / float(diff_p))
                    p_p = 1

            if camera_h < -180:
                camera_h = (180 - (camera_h + 180))
            elif camera_h > 180:
                camera_h = (-180 + (camera_h - 180))

          #heading
            if abs(diff_h) < .5:
                dest_h = target_h
            elif diff_h > 180 or (diff_h < 0 and diff_h > -180):
                dest_h = camera_h+(.5*p_h)
                #if dest_h > target_h:
                #    dest_h = target_h
            elif diff_h <= -180 or (diff_h > 0 and diff_h <= 180):
                dest_h = camera_h-(.5*p_h)
                #if dest_h < target_h:
                #    dest_h = target_h
            else:
                dest_h = target_h

          #pitch
            if abs(diff_p) < .5:
                dest_p = target_p
            elif target_p > camera_p:
                dest_p = camera_p+(.5*p_p)
            elif target_p < camera_p:
                dest_p = camera_p-(.5*p_p)
            else:
                dest_p = target_p

            if camera_h == target_h:
                self.pan_tar+=1
                return Task.cont

            base.camera.setH(dest_h)
            base.camera.setP(dest_p)
        return Task.cont


