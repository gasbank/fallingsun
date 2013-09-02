import struct

class RemoteDisconnectionError(StandardError):
    pass

class Connection(object):
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket
        self.disconnected = False
        
    def sendPacket(self, pktDump):
        pktDumpLen = struct.pack('i', len(pktDump))
        self.clientSocket.send(pktDumpLen + pktDump)
    
    def recvPacket(self):
        pktDumpLen = struct.unpack('i', self.clientSocket.recv(4))[0]
        return self.clientSocket.recv(pktDumpLen)

    def disconnect(self):
        if self.disconnected:
            raise RuntimeError("Unexpected call")
        self.disconnected = True
        self.clientSocket.close()
