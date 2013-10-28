from actor import SActor, ActorProperties

class STreasureBox(SActor):
    def __init__(self, world, location, instanceName):
        SActor.__init__(self, instanceName)
        self.world = world
        
        p = ActorProperties(self.__class__.__name__,
                            location=location, instanceName=instanceName,
                            staticSprite=True)
                
        self.world.send((self.channel, 'JOIN', p))
