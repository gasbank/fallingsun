from actor import SActor, ActorProperties, NamedTasklet, UnknownMessageError
from user import SUser
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from stacklesssocket import stdsocket as socket, install, uninstall
import weakref
from connection import Connection

class SServer(SActor):
    
    def __init__(self, world, instanceName):
        SActor.__init__(self, instanceName)
        self.world = world
        self.users = weakref.WeakValueDictionary()
        
        NamedTasklet(self.startServerLoop)()

        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))
        
    def startServerLoop(self):

        install(0)
        try:
            self.startServerLoopInner()
        finally:
            self.info('Server loop about to exit.')
            uninstall()
    
    def startServerLoopInner(self):
        address = "", 3000
        
        listenSocket = socket.socket(AF_INET, SOCK_STREAM)
        listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listenSocket.bind(address)
        listenSocket.listen(5)
        
        self.listenSocket = listenSocket

        self.info('Listening %s:%d.' % address)   
        while 1:
            self.info('Wait for a remote connection...')
            
            try:
                currentSocket, clientAddress = listenSocket.accept()
            except socket.error:
                return
            
            self.info('Socket %d connected from %s.' % (currentSocket.fileno(),
                                                        clientAddress))
            
            user = SUser(self.world, '%s[%d]' % clientAddress,
                         Connection(currentSocket)).channel
            self.users[id(user)] = user
                    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'CLOSE_SOCKET':
            self.listenSocket._sock.close()
            for _, u in self.users.iteritems():
                u.send((self.channel, msg))
        else:
            raise UnknownMessageError(msg, sentFrom);
