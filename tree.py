import logging
from actor import SActor, ActorProperties

class STree(SActor):
    def __init__(self, world, gatheringName, location=(0,0), hitpoints=5, instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.world = world
        self.hitpoints = hitpoints
        self.havestable = self.hitpoints > 0
        self.gatheringName = gatheringName
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         hitpoints=self.hitpoints,
                                         havestable=self.havestable)))
        
        logging.info('A tree [%s] created.' % self.instanceName)
        
    def getTaskletName(self):
        return self.instanceName
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            pass
        elif msg == "HAVEST":
            
            if self.hitpoints > 0:
                #print self.channel, "--ACQUIRE-->", sentFrom
                sentFrom.send((self.channel, "ACQUIRE", self.gatheringName, 1))
                self.setHitpoints(self.hitpoints - 1)
            
            if self.hitpoints <= 0:
                #print self.channel, "--KILLME-->", self.world
                self.world.send((self.channel, "KILLME"))
                self.deathReason = 'DEPLETED'
            
    def setHitpoints(self, newValue):
        self.hitpoints = newValue
        self.world.send_sequence(((self.channel, "UPDATE_MY_HP", self.hitpoints),
                                  (self.channel, "UPDATE_HAVESTABLE", self.hitpoints > 0)))