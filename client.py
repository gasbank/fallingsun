from actor import SActor, ActorProperties, NamedTasklet
from blank import SBlank
from socket import AF_INET, SOCK_STREAM
from stacklesssocket import stdsocket as socket, install, uninstall
import cPickle

class SClient(SActor):
    def __init__(self, world, instanceName, serverAddress):
        SActor.__init__(self, instanceName)
        self.world = world
        self.serverAddress = serverAddress
        self.blankActors = {}
        
        NamedTasklet(self.startClientLoop)()
        
        self.world.send((self.channel, 'JOIN',
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))

    def startClientLoop(self):

        install(0)
        try:
            self.startClientLoopInner()
        finally:
            self.info('Client loop about to exit.')
            uninstall()
    

    def startClientLoopInner(self):
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        
        try:
            self.socket.connect(self.serverAddress)
        except socket.error:
            self.warn('Connect to %s:%d failed.' % self.serverAddress)
            return
            
        while 1:
            try:
                f = self.socket.makefile('rb', 512)
                cmd, cmdArgs = cPickle.load(f)
                f.close()
            except socket.error:
                self.info('socket.error exception detected.')
                break
            
            self.processMessageMethod((self.socket, cmd, cmdArgs))
            

    def despawnAllBlankActors(self):
        while self.blankActors:
            _, a = self.blankActors.popitem()
            a.channel.send((self.channel, 'KILL_YOURSELF'))
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'CLOSE_SOCKET':
            self.info('CLOSE_SOCKET detected.')
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
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));