from actor import SActor, ActorProperties

class SHome(SActor):
    def __init__(self, world, location=(0,0), instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.world = world
        self.location = location
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         hitpoints=100)))
    def getTaskletName(self):
        return self.instanceName
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            pass