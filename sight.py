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
        
    def __init__(self, world, location, instanceName, sightRange, user=None):
        SActor.__init__(self, instanceName)
        self.world = world
        self._sightRange = None
        self.user = user
        #self.location = location
        self.time = 0
        self.deltaTime = 0
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         instanceName=self.instanceName,
                                         physical=False)))
        self.sightRange = sightRange
    
    def handleWorldState(self, ws, myProp):
        
        self.deltaTime = ws.time - self.time
        self.time = ws.time
        
        #self.location = myProp.location
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            self.handleWorldState(*msgArgs)
        elif msg == 'COLLISION':
            pass
        elif msg == 'NEIGHBORS_LEFT':
            self.user.send((self.channel, 'SEND_DESPAWN', msgArgs[0]))
            
        elif msg == 'NEIGHBORS_ENTERED':
            self.user.send((self.channel, 'SEND_SPAWN', msgArgs[0]))
            
        elif msg == 'KILL_YOURSELF':
            self.world.send((self.channel, 'KILLME'))
            
        elif msg == 'YOU_ARE_DEAD':
            pass
        
        elif msg == 'UPDATE_VECTOR_OF_NEIGHBORS':
            a, p = msgArgs[0]
            self.user.send((self.channel, 'SEND_UPDATE_VECTOR', a, p))
        elif msg == 'MOVE_PAWN':
            direction, pressed = msgArgs
            if pressed: return
            
            if direction == 'N':
                dLoc = (0,-32)
            elif direction == 'E':
                dLoc = (32,0)
            elif direction == 'S':
                dLoc = (0,32)
            elif direction == 'W':
                dLoc = (-32,0)
            else:
                raise RuntimeError('Unknown direction %s', direction)
            
            self.world.send((self.channel, 'REQUEST_RELATIVE_TELEPORT', dLoc))
        elif msg == 'TELEPORTED':
            newLoc = msgArgs[0]
            print newLoc
            self.world.send((self.channel, 'QUERY_RECT_RANGE',
                             newLoc, self.sightRange))
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
        