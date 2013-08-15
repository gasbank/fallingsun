from actor import SActor, ActorProperties

class SHome(SActor):
    def __init__(self, world, location=(0,0), instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.world = world
        self.location = location
        self.gatherings = {}
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         hitpoints=10)))
    def getTaskletName(self):
        return self.instanceName
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            pass
        
        elif msg == "COLLISION":
            if self.channel is msgArgs[0]:
                target = msgArgs[1]
                #targetProp = msgArgs[1+2]
            elif self.channel is msgArgs[1]:
                raise RuntimeError("What happened?")
                target = msgArgs[0]
                #targetProp = msgArgs[0+2]
            else:
                raise RuntimeError("What happened?")
                
            target.send((self.channel, "ADD_STAMINA", 0.1))
            target.send((self.channel, "CAN_STOCK_GATHERINGS"))
            
        elif msg == 'ACQUIRE':
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            
            if self.gatherings.has_key(gathering):
                self.gatherings[gathering] += gatheringCount
            else:
                self.gatherings[gathering] = gatheringCount
                
            print "%s got %d %s. Now have %d" % (self.instanceName, gatheringCount, gathering, self.gatherings[gathering])
            
            sentFrom.send((self.channel, 'CAN_BUILD', 'HOME'))
            
        elif msg == 'GIVE_ME_GATHERINGS':
            
            requests = msgArgs[0]
            reply = {}
            for k,v in requests:
                
                if self.gatherings.has_key(k) and self.gatherings[k] >= v:
                    
                    self.gatherings[k] -= v
                    reply[k] = v
                    
                else:
                    reply = None
                    break
                    
            if reply is not None:
                sentFrom.send((self.channel, 'ACQUIRE', reply))
            