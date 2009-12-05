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

game_started = False

class World(DirectObject):
    def __init__(self):
        base.disableMouse()
        render.setShaderAuto()
        self._setup_models()
        self._setup_lights()
        self._setup_actions()
        self._setup_cam()

    def _setup_cam(self):
        base.camera.setPos(self.env.find("**/camera_loc").getPos())
        base.camera.lookAt(self.env.find("**/camera_start_look").getPos())

    def _setup_models(self):
        self.player = player.Player()
#        self.enemy = cat.Cat((2,2,5))
        #self.env = loader.loadModel(os.path.join("models", "environment"))
        base.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerEvent()
        self.cHandler.setInPattern("artifact_gotten") #artifact gotten?
        
        self.rooms = []
        self.enemylist = []
        self._room2()
        #self.env = loader.loadModel("models/environment")
        #self.envscale = 3
        #self.env.setScale(self.envscale)
        #self.env.reparentTo(render)
        #self.env.setPos(0, 0, 3)
        
        #self._spawn_enemy((2,2,5),"data/testpoint.txt")
        
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
                self._sphere = CollisionSphere(p[0] /self.envscale, p[1]/self.envscale, p[2], 1)
                self._coll_sphere = CollisionNode('collision-point-sphere')
                self._coll_sphere.addSolid(self._sphere)
                self._coll_sphere.setFromCollideMask(BitMask32.bit(0))
                self._coll_sphere.setIntoCollideMask(BitMask32.bit(5))
                self._coll_sphere_path = self.env.attachNewNode(self._coll_sphere)
                self._coll_sphere_path.show()
                self._coll_trav.addCollider(self._coll_sphere_path, self._sphere_handler)
        self.enemylist.append(enemy)
        
    def _room2(self):
        self.env = loader.loadModel("models/room2")
        self.envscale = 3
        self.env.setScale(self.envscale * settings.GLOBAL_SCALE)
        self.env.reparentTo(render)
        self.env.setPos(0, 0, 5)
        self.rooms.append(self.env)
        self._spawn_enemy((0,8,5), "data/room2.txt")

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
