import cPickle
import abc
import socket
from actor import SActor

class SocketBuffer(object):
    def __init__(self, s, mode, bufSize):
        self.socket = s
        self.mode = mode
        self.bufSize = bufSize
    def __enter__(self):
        self.f = self.socket.makefile(self.mode, self.bufSize)
        return self.f
    def __exit__(self, type, value, traceback):
        self.f.close()

class SNetActor(SActor):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, instanceName):
        SActor.__init__(self, instanceName)
        
    def getReadBuffer(self, bufSize):
        return SocketBuffer(self.getSocket(), 'rb', bufSize)
    
    def getWriteBuffer(self, bufSize):
        return SocketBuffer(self.getSocket(), 'wb', bufSize)
    
    def recvPacket(self):
        with self.getReadBuffer(512) as f:
            return cPickle.load(f)
    
    def sendPacket(self, pkt):
        try:
            with self.getWriteBuffer(512) as f:
                cPickle.dump(pkt, f, cPickle.HIGHEST_PROTOCOL)
        except socket.error:
            self.warn('socket.error exception detected at sendPacket.')

    @abc.abstractmethod            
    def getSocket(self):
        return
