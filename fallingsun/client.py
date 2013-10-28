from actor import ActorProperties, NamedTasklet, UnknownMessageError
from netactor import SNetActor
from blank import SBlank
from socket import AF_INET, SOCK_STREAM
from stacklesssocket import stdsocket as socket, install, uninstall
from connection import Connection
import struct

class SClient(SNetActor):
    def __init__(self, world, instanceName, serverAddress):
        SNetActor.__init__(self, instanceName)
        self.world = world
        self.serverAddress = serverAddress
        self.blankActors = {}
        self.ownedActorId = None
        self.socket = None
        
        NamedTasklet(self.startClientLoop)()
        
        self.world.send((self.channel, 'JOIN',
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))

    def getConnection(self):
        return self.connection

    def startClientLoop(self):

        install(0)
        try:
            self.startClientLoopInner()
        finally:
            self.info('Client loop about to exit.')
            uninstall()
    

    def startClientLoopInner(self):
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        self.connection = Connection(self.socket)
        
        try:
            self.socket.connect(self.serverAddress)
        except socket.error:
            self.warn('Connect to %s:%d failed.' % self.serverAddress)
            return
            
        while 1:
            try:
                cmd, cmdArgs = self.recvCommand()
            except struct.error:
                self.info('struct.error exception detected.')
                break
            except socket.error:
                self.info('socket.error exception detected.')
                break
            
            self.processMessageMethod((self.socket, cmd, cmdArgs))
            

    def despawnAllBlankActors(self):
        while self.blankActors:
            _, a = self.blankActors.popitem()
            #a.channel.send((self.channel, 'KILL_YOURSELF'))
            self.world.send((a.channel, 'KILLME'))
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'CLOSE_SOCKET':
            self.info('CLOSE_SOCKET from %s' % sentFrom)
            self.sendCommand(('BYE'))

            # Cleanup all blank actors if server-side closing
            # of the socket happens. 
            if sentFrom is self.socket:
                self.despawnAllBlankActors()
                
            self.socket.close()
        elif msg == 'SPAWN':
            for actorId, actorType, location, angle, velocity in msgArgs[0]:
                self.blankActors[actorId] = SBlank(self.world, actorType,
                                                   location,
                                                   'Blank(%d)'%actorId,
                                                   velocity, angle)
        elif msg == 'DESPAWN':
            for actorId, in msgArgs[0]:
                self.blankActors[actorId].channel.send((self.channel,
                                                        'KILL_YOURSELF'))
                del self.blankActors[actorId]
        elif msg == 'UPDATE_VECTOR':
            actorId, location, angle, velocity = msgArgs[0]
            self.world.send((self.blankActors[actorId].channel,
                             'UPDATE_VECTOR', angle, velocity))
        elif msg == 'OWNERSHIP':
            self.ownedActorId = msgArgs[0]
            self.info('Ownership set to %d.' % self.ownedActorId)
        elif msg == 'MOVE_PAWN':
            direction, pressed = msgArgs
            
            if direction == 'N': angle = 90*0
            elif direction == 'E': angle = 90*1
            elif direction == 'S': angle = 90*2
            elif direction == 'W': angle = 90*3
            else: raise RuntimeError('Unknown direction %s', direction)
            
            velocity = 2 if pressed else 0
            
            if self.ownedActorId:
                self.sendCommand(('UPDATE_VECTOR', (self.ownedActorId,
                                                   (angle, velocity))))
        elif msg == 'CHAT':
            self.info('Chat received from %s: %s' % (sentFrom, msgArgs[0]))
        elif msg == None:
            pass
        else:
            raise UnknownMessageError(msg, sentFrom);