from actor import SActor, ActorProperties

class SBlank(SActor):
    def __init__(self, world, blankType, location, instanceName, velocity,
                 angle):
        SActor.__init__(self, instanceName)
        self.world = world
        self.blankType = blankType
        self.velocity = velocity
        self.angle = angle
        self.hitpoints = 0
        
        self.debug('Created.')
        
        p = ActorProperties(self.__class__.__name__,
                            location=location, angle=self.angle,
                            velocity=self.velocity, hitpoints=self.hitpoints,
                            animatedSprite=True, blankType=blankType,
                            instanceName=instanceName)
        
        self.world.send((self.channel, 'JOIN', p))
        
    def defaultMessageAction(self, args):
        sentFrom, msg, _ = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'COLLISION':
            pass
        elif msg == 'KILL_YOURSELF':
            self.world.send((self.channel, 'KILLME'))
        elif msg == 'YOU_ARE_DEAD':
            pass
        elif msg == 'NEIGHBORS_ENTERED':
            pass
        elif msg == 'NEIGHBORS_LEFT':
            pass
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
        