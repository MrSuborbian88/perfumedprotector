from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
import os
import main
import sys

class Pregame(DirectObject):
    def __init__(self):
        self.posit = 0
        self.accept('mouse1', self.positionMove)
        self.accept('1', self.selectOne)
        self.accept('2', self.selectTwo)
        self.accept("escape", sys.exit)
        self.a = OnscreenImage(parent=render2d, image=os.path.join("image files", "Title-Screen.png"))
        self.sound_title = loader.loadSfx(os.path.join("sound files", "Title Theme.mp3"))
        self.sound_main = loader.loadSfx(os.path.join("sound files", "Main Theme.mp3"))
        self.sound_title.play()
        self.sound_title.setLoop(True)
        self.dog_selection=0


    def selectOne(self):
        self.dog_selection=1
        self.positionMove()
        
    def selectTwo(self):
        self.dog_selection=2
        self.positionMove()
        
    def positionMove(self):
        self.posit += 1
        if self.posit == 1:
            self.a.destroy()
            self.b = OnscreenImage(parent=render2d, image=os.path.join("image files", "Intro-Screen.png"))
        elif self.posit == 2:
            self.b.destroy()
            self.c = OnscreenImage(parent=render2d, image=os.path.join("image files", "Instruction-Screen.png"))
        elif self.posit == 3:
            self.c.destroy()
            self.d = OnscreenImage(parent=render2d, image=os.path.join("image files", "Selection-Screen.png"))
        elif self.posit == 4:
            if not self.dog_selection==0:
                self.sound_title.stop()
                self.sound_main.play()
                self.sound_main.setLoop(True)
                self.d.destroy()
                w = main.World()
            else:
                self.posit = 3