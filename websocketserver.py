from actor import SActor, ActorProperties, NamedTasklet, UnknownMessageError
from user import SUser
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from stacklesssocket import stdsocket as socket, install, uninstall
import weakref
from webconnection import WebConnection

class SWebSocketServer(SActor):
    
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

        try:
            install(0)
        except StandardError:
            pass
        
        try:
            self.startServerLoopInner()
        finally:
            self.info('Server loop about to exit.')
            uninstall()
    
    def startServerLoopInner(self):
        address = "", 3001
        
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
            
            user = SUser(self.world, '%s[%d][W]' % clientAddress,
                         WebConnection(currentSocket)).channel
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

'''
    def recv_data (self, client):
        # as a simple server, we expect to receive:
        #    - all data at one go and one frame
        #    - one frame at a time
        #    - text protocol
        #    - no ping pong messages
        data = bytearray(client.recv(512))
        if(len(data) < 6):
            raise Exception("Error reading data")
        # FIN bit must be set to indicate end of frame
        assert(0x1 == (0xFF & data[0]) >> 7)
        # data must be a text frame
        # 0x8 (close connection) is handled with assertion failure
        assert(0x1 == (0xF & data[0]))
        
        # assert that data is masked
        assert(0x1 == (0xFF & data[1]) >> 7)
        datalen = (0x7F & data[1])
        
        #print("received data len %d" %(datalen,))
        
        str_data = ''
        if(datalen > 0):
            mask_key = data[2:6]
            masked_data = data[6:(6+datalen)]
            unmasked_data = [masked_data[i] ^ mask_key[i%4] for i in range(len(masked_data))]
            str_data = str(bytearray(unmasked_data))
        return str_data

    def broadcast_resp(self, data):
        # 1st byte: fin bit set. text frame bits set.
        # 2nd byte: no mask. length set in 1 byte. 
        resp = bytearray([0b10000001, len(data)])
        # append the data bytes
        for d in bytearray(data):
            resp.append(d)
            
        self.LOCK.acquire()
        for client in self.clients:
            try:
                client.send(resp)
            except:
                print("error sending to a client")
        self.LOCK.release()
 

 
    
     
    def handle_client (self, client, addr):
        self.handshake(client)
        try:
            while 1:            
                data = self.recv_data(client)
                print("received [%s]" % (data,))
                self.broadcast_resp(data)
        except Exception as e:
            print("Exception %s" % (str(e)))
        print('Client closed: ' + str(addr))
        #self.LOCK.acquire()
        self.clients.remove(client)
        #self.LOCK.release()
        client.close()
        

    def start_server (self, port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(5)
        while(1):
            print ('Waiting for connection...')
            conn, addr = s.accept()
            print ('Connection from: ' + str(addr))
            threading.Thread(target = self.handle_client, args = (conn, addr)).start()
            self.LOCK.acquire()
            self.clients.append(conn)
            self.LOCK.release()
'''