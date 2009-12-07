from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'window-title Doggy Delivery')
loadPrcFileData('', 'notify-level fatal')
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
import player
import cat
#import enemy

import sys
import os

GAME_STARTED = False
ROOM_OFFSETS = [(0,0,0), #placeholder - no room 0
                (0,0,0), #1
                (0,0,0), #2
                (0,0,0), #3
                (0,0,0), #4
                (0,0,0), #placeholder - no room 5
                (0,0,0), #6
                (0,0,0), #7
                (0,0,0), #8
                (0,0,0), #9
                (0,0,0), #10
                (0,0,0), #11
                (0,0,0), #12
                (0,0,0), #13
                (0,0,0), #14
                (0,0,0), #15
                (0,0,0), #16
                (0,0,0), #17
                (0,0,0)] #18
ROOM_LOADS = [(0),              #placeholder - no room 0
              (1,2),            #1
              (1,2,3,4),        #2
              (2,3,6),          #3
              (2,4,6),          #4
              (0),              #placeholder - no room 5
              (3,4,5,7,9),      #6
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
    def __init__(self):
        base.disableMouse()
        render.setShaderAuto()
        self._setup_models()
        self._preload_rooms()
        self._setup_room_collisions()
        self._setup_lights()
        self._setup_actions()
        self._setup_cam()
        self._load_rooms(1)

    def _setup_cam(self):
        base.camera.setPos(self.room2.find("**/camera_loc").getPos())
        base.camera.lookAt(self.room2.find("**/camera_start_look").getPos())

    def _setup_models(self):
        self.player = player.Player()
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
        self.accept("enter",  start_game)

    def _spawn_enemy(self,pos,file_loc):
        self._coll_trav = CollisionTraverser()
        enemy = cat.Cat(pos,file_loc)
        for p in enemy._points:
                self._sphere_handler = CollisionHandlerQueue()
                self._sphere = CollisionSphere(p[0] /settings.ENV_SCALE, p[1]/settings.ENV_SCALE, p[2], 1)
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
        self.room1.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room1.setPos(ROOM_OFFSETS[2][0], ROOM_OFFSETS[2][1], ROOM_OFFSETS[2][2])
        self.rooms.append(self.room1)

        self.room2 = loader.loadModel("models/room2")
        self.room2.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room2.setPos(ROOM_OFFSETS[2][0], ROOM_OFFSETS[2][1], ROOM_OFFSETS[2][2])
        self.rooms.append(self.room2)

        #load room1 and room2 to start
        #self.room1.reparentTo(self.env)
        self.room2.reparentTo(self.env)

        self.room3 = loader.loadModel("models/room3")
        self.room3.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room3.setPos(ROOM_OFFSETS[3][0], ROOM_OFFSETS[3][1], ROOM_OFFSETS[3][2])
        self.rooms.append(self.room3)

        self.room4 = loader.loadModel("models/room4")
        self.room4.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room4.setPos(ROOM_OFFSETS[4][0], ROOM_OFFSETS[4][1], ROOM_OFFSETS[4][2])
        self.rooms.append(self.room4)

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

        self.room14 = loader.loadModel("models/room14")
        self.room14.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room14.setPos(ROOM_OFFSETS[14][0], ROOM_OFFSETS[14][1], ROOM_OFFSETS[14][2])
        self.rooms.append(self.room14)

        self.room15 = loader.loadModel("models/room15")
        self.room15.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room15.setPos(ROOM_OFFSETS[15][0], ROOM_OFFSETS[15][1], ROOM_OFFSETS[15][2])
        self.rooms.append(self.room15)

        self.room16 = loader.loadModel("models/room16")
        self.room16.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room16.setPos(ROOM_OFFSETS[16][0], ROOM_OFFSETS[16][1], ROOM_OFFSETS[16][2])
        self.rooms.append(self.room16)

        self.room17 = loader.loadModel("models/room17")
        self.room17.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room17.setPos(ROOM_OFFSETS[17][0], ROOM_OFFSETS[17][1], ROOM_OFFSETS[17][2])
        self.rooms.append(self.room17)

        self.room18 = loader.loadModel("models/room18")
        self.room18.setScale(settings.ENV_SCALE * settings.GLOBAL_SCALE)
        self.room18.setPos(ROOM_OFFSETS[18][0], ROOM_OFFSETS[18][1], ROOM_OFFSETS[18][2])
        self.rooms.append(self.room18)
        """

def start_game():
    b.destroy()
    d.destroy()
    textObject.destroy()

if __name__ == '__main__':
    bk_text = "Plague of the Perfumed Protector"
    font = loader.loadFont(os.path.join("fonts", "arial.ttf"))
    font.setPixelsPerUnit(200)
    """
    textObject = OnscreenText(text=bk_text, font=font, pos = (0, 0.7),
                              scale=0.2, fg=(1, 1, 1, 1),
                              mayChange=0)
    b = DirectButton(text="Start Game", text_font=font, clickSound=None,
                     command=start_game, text_fg=(0, 0, 0, 1), scale=.1,
                     pos=(0, 0, -.5), relief=None)
    b.setTransparency(1)
    d = DirectButton(text="Quit", text_font=font, clickSound=None,
                     command=sys.exit, text_fg=(0, 0, 0, 1), scale=.1,
                     pos=(0, 0, -.62), relief=None)
    d.setTransparency(1)
    """
    #c = OnscreenImage(parent=render2d, image=os.path.join("models", "background.png"))
    #sound_ambient = loader.loadSfx(os.path.join("sounds", "ambient-wind.mp3"))
    #sound_ambient.play()
    #sound_ambient.setLoop(True)

    w = World()
    run()
