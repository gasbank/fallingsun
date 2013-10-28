import logging
from actor import SActor, ActorProperties

class STree(SActor):
    @property
    def hitpoints(self):
        return self._hitpoints
    @hitpoints.setter
    def hitpoints(self, value):
        self._hitpoints = value
        self.world.send_sequence(((self.channel, "UPDATE_MY_HP",
                                   self._hitpoints),
                                  (self.channel, "UPDATE_HARVESTABLE",
                                   self._hitpoints > 0)))
        
        if self.hitpoints <= 0:
            logging.debug('%s --%s--> %s' % (self.channel, 'KILLME', self.world))
            self.world.send((self.channel, "KILLME"))
            self.deathReason = 'DEPLETED'
        
    @property
    def harvestable(self):
        return self.hitpoints > 0
            
    def __init__(self, world, gatheringName, location=(0,0),
                 hitpoints=5, instanceName='', hitpointsDecay=0):
        
        SActor.__init__(self, instanceName)
        self.world = world
        self._hitpoints = None
        self.gatheringName = gatheringName
        self.hitpointsDecay = hitpointsDecay
        
        vocas = set(['HARVEST', 'DESTROY', 'CULTIVATE'])
        
        self.debug('Created.')
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         harvestable=self.harvestable,
                                         staticSprite=True,
                                         instanceName=self.instanceName,
                                         vocas=vocas)))
        
        self.hitpoints = hitpoints
                
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            if self.hitpointsDecay > 0:
                self.setHitpoints(self.hitpoints - self.hitpointsDecay)

        elif msg == "HARVEST":
            
            if self.hitpoints > 0:
                logging.debug('%s --%s--> %s' % (self.channel, 'ACQUIRE', sentFrom))
                sentFrom.send((self.channel, "ACQUIRE", self.gatheringName, 1))
                self.hitpoints -= 1
                
                
