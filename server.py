from actor import SActor, ActorProperties, NamedTasklet
from user import SUser
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from stacklesssocket import stdsocket as socket, install, uninstall
import weakref

class RemoteDisconnectionError(StandardError):
    pass

class Connection:
    disconnected = False

    def __init__(self, serverActor, clientSocket, clientAddress):
        self.serverActor = serverActor
        self.clientSocket = clientSocket
        self.clientAddress = clientAddress

        self.readBuffer = ""

        self.userID = id(SUser(serverActor.world, '%s[%d]' % clientAddress,
                               self))

    def Disconnect(self):
        if self.disconnected:
            raise RuntimeError("Unexpected call")
        self.disconnected = True
        self.clientSocket.close()

    def Write(self, s):
        self.clientSocket.send(s)

    def WriteLine(self, s):
        self.Write(s +"\r\n")

    def ReadLine(self):
        global server
    
        s = self.readBuffer
        while True:
            # If there is a CRLF in the text we have, we have a full
            # line to return to the caller.
            if s.find('\r\n') > -1:
                i = s.index('\r\n')
                # Strip the CR LF.
                line = s[:i]
                self.readBuffer = s[i+2:]
                while '\x08' in line:
                    i = line.index('\x08')
                    if i == 0:
                        line = line[1:]
                    else:
                        line = line[:i-1] + line[i+1:]
                return line

            # An empty string indicates disconnection.
            v = self.clientSocket.recv(1000)
            if v == "":
                #print 'haha'
                self.disconnected = True
                raise RemoteDisconnectionError
            s += v

class SServer(SActor):
    
    def __init__(self, world, instanceName):
        SActor.__init__(self, instanceName)
        self.world = world
        self.userIndex = weakref.WeakValueDictionary()
        
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
            
            Connection(self, currentSocket, clientAddress)
                    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'CLOSE_SOCKET':
            self.listenSocket._sock.close()
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
                               
    def RegisterUser(self, user):
        self.userIndex[id(user)] = user
        
    def ListUsers(self):
        return [ v for v in self.userIndex.itervalues() ]