import cPickle
import json
import abc
import socket
import struct
from actor import SActor

class SNetActor(SActor):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, instanceName):
        SActor.__init__(self, instanceName)

    def recvCommand(self):
        return json.loads(self.getConnection().recvPacket())
    
    def sendCommand(self, cmdTuple):
        try:
            pkt = json.dumps(cmdTuple)
            self.getConnection().sendPacket(pkt)
        except socket.error:
            self.warn('socket.error exception detected at sendCommand.')
            
    @abc.abstractmethod            
    def getConnection(self):
        return
