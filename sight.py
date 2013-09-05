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
    @property
    def display(self):
        return self._display
    @display.setter
    def display(self, value):
        self._display = value
        
    def __init__(self, world, location, instanceName, sightRange, user=None):
        SActor.__init__(self, instanceName)
        self.world = world
        self._sightRange = None
        self.user = user
        #self.location = location
        self.time = 0
        self.deltaTime = 0
        self._display = None
        
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
            #self.info('MOVE_PAWN detected.')
            
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
            
            #self.info('REQUEST_RELATIVE_TELEPORT about to send...')
            self.world.send((self.channel, 'REQUEST_RELATIVE_TELEPORT', dLoc))
            #self.info('REQUEST_RELATIVE_TELEPORT sent!')
        elif msg == 'TELEPORTED':
            newLoc = msgArgs[0]
            #self.info('TELEPORTED detected.')
            #self.info('QUERY_RECT_RANGE about to send...')
            self.world.send((self.channel, 'QUERY_RECT_RANGE',
                             newLoc, self.sightRange))
            #self.info('QUERY_RECT_RANGE sent!')
        elif msg == 'QUERY_RESULT':
            #self.info('QUERY_RESULT detected.')
            
            if self.display:
                self.display.send((self.channel, 'SIGHTED_ACTORS', msgArgs[0]))
        elif msg == 'I_AM_DISPLAY':
            self.display = sentFrom
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
        