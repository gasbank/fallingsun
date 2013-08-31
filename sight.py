from actor import SActor, ActorProperties

class SSight(SActor):
    @property
    def sightRange(self):
        return self._sightRange
    @sightRange.setter
    def sightRange(self, value):
        newValue = max(0, min(value, 20))
        if self._sightRange == newValue: return
        self._sightRange = newValue
        self.world.send((self.channel, "SIGHT_RANGE", newValue))
        
    def __init__(self, world, location, instanceName, sightRange, user):
        SActor.__init__(self, instanceName)
        self.world = world
        self._sightRange = None
        self.user = user
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         instanceName=self.instanceName,
                                         physical=False)))
        self.sightRange = sightRange
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'COLLISION':
            pass
        elif msg == 'NEIGHBORS_LEFT':
            self.user.send((self.channel, 'DESPAWN', msgArgs[0]))
            
        elif msg == 'NEIGHBORS_ENTERED':
            self.user.send((self.channel, 'SPAWN', msgArgs[0]))
            
        elif msg == 'KILL_YOURSELF':
            self.world.send((self.channel, 'KILLME'))
            
        elif msg == 'YOU_ARE_DEAD':
            pass
        
        elif msg == 'UPDATE_VECTOR_OF_NEIGHBORS':
            a, p = msgArgs[0]
            self.user.send((self.channel, 'UPDATE_VECTOR', a, p))
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
        