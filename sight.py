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
        
    def __init__(self, world, location, instanceName, sightRange):
        SActor.__init__(self, instanceName)
        self.world = world
        self._sightRange = None
        
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
            self.info('Left - %s' % msgArgs[0])
        elif msg == 'NEIGHBORS_ENTERED':
            self.info('Entered - %s' % msgArgs[0])
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
        