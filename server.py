from actor import SActor, ActorProperties, NamedTasklet
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from stacklesssocket import stdsocket as socket, install, uninstall

class SServer(SActor):
    def __init__(self, world, instanceName):
        SActor.__init__(self, instanceName)
        self.world = world
        
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
        address = "127.0.0.1", 3000
        '''
        info = -12345678
        data = struct.pack("i", info)
        dataLength = len(data)
        '''
        
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
            
            self.info('Server about to close connection %d'
                      % currentSocket.fileno())
            currentSocket.close()
            
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'CLOSE_LISTENING_SOCKET':
            self.listenSocket._sock.close()
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));