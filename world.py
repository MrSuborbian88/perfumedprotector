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
ROOM_OFFSETS = [(0,0,0),            #placeholder - no room 0
                (547,0,0),          #1
                (0,0,0),            #2
                (190,-486,0),       #3
                (388,565,0),        #4
                (0,0,0),            #placeholder - no room 5
                (1077,79,0),        #6 83
                (1580,-540,0),      #7
                (1800,-500,0),      #8
                (1780,79,0),        #9
                (2300,-300,0),      #10
                (2500,-800,0),      #11
                (2800,-300,0),      #12
                (3100,0,0)]         #13

ROOM_LOADS = [(0),              #placeholder - no room 0
              (1,2),            #1
              (1,2,3,4),        #2
              (2,3,6),          #3
              (2,4,6),          #4
              (0),              #placeholder - no room 5
              (3,4,6,7,9),      #6
              (6,7,8),          #7
              (7,8,9,10,11),    #8
              (6,8,9,10),       #9
              (8,9,10,11,12),   #10
              (8,10,11,12),     #11
              (10,11,12,13),    #12
              (12,13)]          #13

class World(DirectObject):
    def __init__(self, dogSelection):
        base.disableMouse()
        render.setShaderAuto()
        self.sound = True
        self.dogSelection = dogSelection
        self.current_room = 1
        self.pan_tar = 1
        self._setup_models()
        self._preload_rooms()
        self._preload_enemies()
        self._setup_room_collisions()
        self._setup_lights()
        self._setup_actions()
        self._setup_cam()
        self._load_rooms(2)
        self._change_enemies(1)

        taskMgr.doMethodLater(2, self.camera_pan, "cam_pan")

    def _setup_cam(self):
        base.camera.setPos(self.room1.find("**/camera_loc").getPos() + ROOM_OFFSETS[1])
        base.camera.lookAt(self.room1.find("**/camera_start_look").getPos() + ROOM_OFFSETS[1])

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
                self._sphere = CollisionSphere(p[0], p[1], p[2], 2 * settings.GLOBAL_SCALE)
                self._coll_sphere = CollisionNode('collision-point-sphere')
                self._coll_sphere.addSolid(self._sphere)
                self._coll_sphere.setFromCollideMask(BitMask32.allOff())
                self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
                self._coll_sphere_path = self.env.attachNewNode(self._coll_sphere)
                self._coll_sphere_path.show()
                self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        return enemy
        
    def _spawn_cat(self,pos,file_loc):
        self._coll_trav = CollisionTraverser()
        enemy = cat.Cat(pos,file_loc)
        for p in enemy._points:
                self._sphere_handler = CollisionHandlerQueue()
                #self._sphere = CollisionSphere(p[0]/settings.ENV_SCALE, p[1]/settings.ENV_SCALE, p[2], 2 * settings.ENV_SCALE)
                self._sphere = CollisionSphere(p[0], p[1], p[2],1 * settings.GLOBAL_SCALE)
                self._coll_sphere = CollisionNode('collision-point-sphere')
                self._coll_sphere.addSolid(self._sphere)
                self._coll_sphere.setFromCollideMask(BitMask32.allOff())
                self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
                self._coll_sphere_path = self.env.attachNewNode(self._coll_sphere)
                self._coll_sphere_path.show()
                self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        return enemy
        
    def _setup_room_collisions(self): 
        self.cTrav = CollisionTraverser()
        # Front collision
        self._room_check_handler = CollisionHandlerQueue()
        self._room_check_ray = CollisionRay()
        self._room_check_ray.setOrigin(0, -5, 1)
        self._room_check_ray.setDirection(0, 0, -1)
        self._room_check_coll = CollisionNode('collision-ground-front')
        self._room_check_coll.addSolid(self._room_check_ray)
        self._room_check_coll.setFromCollideMask(BitMask32(0x00000001))
        self._room_check_coll.setIntoCollideMask(BitMask32.allOff())
        self._room_check_coll_path = self.player._model.attachNewNode(self._room_check_coll)
        self._room_check_coll_path.show()
        self.cTrav.addCollider(self._room_check_coll_path, self._room_check_handler)

        taskMgr.doMethodLater(1, self._handle_room_check_collisions, "room_check")

    def _handle_room_check_collisions(self, task):
        self.cTrav.traverse(self.env)
        for i in range(self._room_check_handler.getNumEntries()):
            entry = self._room_check_handler.getEntry(i)
        #In room 1
            if entry.getIntoNodePath() == self.room1 or \
                    entry.getIntoNodePath().getParent() == self.room1 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room1:
                print "1"
                self._change_room(1)
        #In room 2
            if entry.getIntoNodePath() == self.room2 or \
                    entry.getIntoNodePath().getParent() == self.room2 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room2:
                print "2"
                self._change_room(2)
        #In room 3
            elif entry.getIntoNodePath() == self.room3 or \
                    entry.getIntoNodePath().getParent() == self.room3 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room3:
                print "3"
                self._change_room(3)
        #In room 4
            elif entry.getIntoNodePath() == self.room4 or \
                    entry.getIntoNodePath().getParent() == self.room4 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room4:
                print "4"
                self._change_room(4)
        #In room 6
            elif entry.getIntoNodePath() == self.room6 or \
                    entry.getIntoNodePath().getParent() == self.room6 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room6:
                print "6"
                self._change_room(6)
        #In room 7
            elif entry.getIntoNodePath() == self.room7 or \
                    entry.getIntoNodePath().getParent() == self.room7 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room7:
                print "7"
                self._change_room(7)
        #In room 8
            elif entry.getIntoNodePath() == self.room8 or \
                    entry.getIntoNodePath().getParent() == self.room8 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room8:
                print "8"
                self._change_room(8)
        #In room 9
            elif entry.getIntoNodePath() == self.room9 or \
                    entry.getIntoNodePath().getParent() == self.room9 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room9:
                print "9"
                self._change_room(9)
        #In room 10
            elif entry.getIntoNodePath() == self.room10 or \
                    entry.getIntoNodePath().getParent() == self.room10 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room10:
                print "10"
                self._change_room(10)
        #In room 11
            elif entry.getIntoNodePath() == self.room11 or \
                    entry.getIntoNodePath().getParent() == self.room11 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room11:
                print "11"
                self._change_room(11)
        #In room 12
            elif entry.getIntoNodePath() == self.room12 or \
                    entry.getIntoNodePath().getParent() == self.room12 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room12:
                print "12"
                self._change_room(12)
        #In room 13
            elif entry.getIntoNodePath() == self.room13 or \
                    entry.getIntoNodePath().getParent() == self.room13 or \
                    entry.getIntoNodePath().getParent().getParent() == self.room13:
                print "13"
                self._change_room(13)
                 
        return Task.again

    def _change_room(self, num):
        if self.current_room != num:
            self.current_room = num
           #change camera
            base.camera.setPos(self.rooms[num].find("**/camera_loc").getPos() + ROOM_OFFSETS[num])
            base.camera.lookAt(self.rooms[num].find("**/camera_start_look").getPos() + ROOM_OFFSETS[num])
            self._load_rooms(num)
            self._change_enemies(num)
            
    def _change_enemies(self,num):
        for e in self._current_en:
            e._model.detachNode()
        self._current_en = self._en_list[num]
        print self._current_en
        for e in self._current_en:
            e._model.reparentTo(render)
    def _load_rooms(self, current):
        self.room1.detachNode()
        self.room2.detachNode()
        self.room3.detachNode()
        self.room4.detachNode()
        self.room6.detachNode()
        self.room7.detachNode()
        self.room8.detachNode()
        self.room9.detachNode()
        self.room10.detachNode()
        self.room11.detachNode()
        self.room12.detachNode()
        self.room13.detachNode()
        
        for r in ROOM_LOADS[current]:
            print "loading room %d" % r
            self.rooms[r].reparentTo(self.env)

    def _preload_rooms(self):
        self.rooms.append(NodePath())

        self.room1 = loader.loadModel("models/room1")
        self.room1.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room1.setPos(ROOM_OFFSETS[1][0], ROOM_OFFSETS[1][1], ROOM_OFFSETS[1][2])
        self.rooms.append(self.room1)

        self.room2 = loader.loadModel("models/room2")
        self.room2.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room2.setPos(ROOM_OFFSETS[2][0], ROOM_OFFSETS[2][1], ROOM_OFFSETS[2][2])
        self.rooms.append(self.room2)

        #load room1 and room2 to start
        self.room1.reparentTo(self.env)
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

        self.rooms.append(NodePath())

        self.room6 = loader.loadModel("models/room6")
        self.room6.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room6.setPos(ROOM_OFFSETS[6][0], ROOM_OFFSETS[6][1], ROOM_OFFSETS[6][2])
        self.rooms.append(self.room6)

        self.room7 = loader.loadModel("models/room7")
        self.room7.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room7.setPos(ROOM_OFFSETS[7][0], ROOM_OFFSETS[7][1], ROOM_OFFSETS[7][2])
        self.room7.setH(-136)
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
        
    def _preload_enemies(self):
        self._en_list = { }
        e1 = []
        self._en_list[1] = e1

        e2 = []
        e2.append(self._spawn_enemy((8,119,40), "data/r2_g1.txt"))
        self._en_list[2] = e2
        
        e3 = []
        e3.append(self._spawn_cat((840,-425,10), "data/r3_c1.txt"))
        self._en_list[3] = e3

        e4 = []

        self._en_list[4] = e4

        e5 = []

        self._en_list[5] = e5

        e6 = []

        self._en_list[6] = e6


        e7 = []

        self._en_list[7] = e7

        e8 = []
        
        self._en_list[8] = e8

        e9 = []

        self._en_list[9] = e9

        e10 = []

        self._en_list[10] = e10

        e11 = []

        self._en_list[11] = e11

        e12 = []

        self._en_list[12] = e12
        self._current_en = e1

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
        else:
            self.pan_tar = 1
        return Task.cont
