from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from pandac.PandaModules import BaseParticleEmitter,BaseParticleRenderer
from pandac.PandaModules import PointParticleFactory,SpriteParticleRenderer
import os

GLOBAL_SCALE = 9
ENV_SCALE = 3

PLAYER_WALK_RATE = 20 * GLOBAL_SCALE
PLAYER_ROTATION_RATE = 300
PLAYER_CHASE_LENGTH = 500
ENEMY_WALK_RATE = 5 * GLOBAL_SCALE
ENEMY_ROTATION_RATE = 250

def loadParticleConfig(position):
        p = ParticleEffect()
        p.loadConfig(os.path.join("models", "smokering.ptf"))   
        p.accelerate(.25) 
        p.setPos(position) 
        p.reparentTo(render) 
        p.setScale(30)  
        p.start()
        #taskMgr.doMethodLater(5, self.cleanParticles, 'Stop Particles')
        
def cleanParticles(p, random):
        p.softStop()