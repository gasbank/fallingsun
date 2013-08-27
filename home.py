import stackless  # @UnresolvedImport
from actor import SActor, ActorProperties, NamedTasklet, NamedChannel

class SHome(SActor):
    def __init__(self, world, location=(0,0), instanceName="", staminaRefillSpeed=6):
        SActor.__init__(self, instanceName)
        self.time = 0
        self.deltaTime = 0
        self.world = world
        self.location = location
        self.gatherings = {}
        self.staminaRefillSpeed = staminaRefillSpeed
        self.tasklets = {}
        self.debug('Created.')
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         staticSprite=True,
                                         hitpoints=10,
                                         instanceName=self.instanceName)))
    
    def taskAddStamina(self, channel, target):
        while 1:
            startTime = self.time
            while self.time - startTime < 5:
                channel.receive()
                
            target.send((self.channel, 'ADD_STAMINA', self.staminaRefillSpeed))
            
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            self.deltaTime = msgArgs[0].time - self.time
            self.time = msgArgs[0].time
            
            for k,v in self.tasklets.iteritems():
                v.send(None)
            
        elif msg == 'COLLISION':
            pass
            
        elif msg == 'ACQUIRE':
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            
            self.gatherings[gathering] = self.gatherings.get(gathering, 0) + gatheringCount
                
            self.info('%d %s acquired. Now have %d.'
                      % (gatheringCount, gathering, self.gatherings[gathering]))
            
        elif msg == 'GIVE_ME_GATHERINGS':
            
            requests = msgArgs[0]
            reply = {}
            for k in list(requests):
                
                if self.gatherings.get(k, 0) >= requests[k]:
                    
                    self.gatherings[k] = self.gatherings.get(k, 0) - requests[k]
                    reply[k] = requests[k]
                    
            sentFrom.send((self.channel, 'ACQUIRE', reply))
        
        elif msg == 'NEIGHBORS_LEFT':
            self._neighbors.difference_update(msgArgs[0])
            self.debug('Left:%s'%msgArgs[0])
            for newlyLeft in msgArgs[0]:
                cname = str(newlyLeft)+':AddStamina'
                self.tasklets[cname].send_exception(TaskletExit)
                del self.tasklets[cname]
        elif msg == 'NEIGHBORS_ENTERED':
            self._neighbors.update(msgArgs[0])
            self.debug('Entered:%s'%msgArgs[0])
            for newlyEntered in msgArgs[0]:
                c = NamedChannel()
                c.name = str(newlyEntered)+':AddStamina'
                self.tasklets[c.name] = c
                NamedTasklet(self.taskAddStamina)(c, newlyEntered)
