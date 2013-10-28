import hashlib
import base64
from connection import Connection, RemoteDisconnectionError
import logging

class WebConnection(Connection):

    def __init__(self, clientSocket):
        self.disconnected = False
        self.clientSocket = clientSocket
        self.MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.HSHAKE_RESP = "HTTP/1.1 101 Switching Protocols\r\n" + \
                "Upgrade: websocket\r\n" + \
                "Connection: Upgrade\r\n" + \
                "Sec-WebSocket-Accept: %s\r\n" + \
                "\r\n"
        
        self.handshake()

    def handshake(self):
        logging.debug('Handshaking...')
        data = self.clientSocket.recv(2048)
        headers = self.parse_headers(data)
        logging.debug('Got headers:')
        for k, v in headers.iteritems():
            logging.debug('%s : %s' % (k, v))
            
        if headers.has_key('Sec-WebSocket-Key'):
            key = headers['Sec-WebSocket-Key']
            resp_data = self.HSHAKE_RESP % ((base64.b64encode(hashlib.sha1(key+self.MAGIC).digest()),))
            logging.debug('Response: [%s]' % (resp_data,))
            return self.clientSocket.send(resp_data)
        else:
            self.clientSocket.close()

    def parse_headers(self, data):
        headers = {}
        lines = data.splitlines()
        if lines:
            for l in lines:
                parts = l.split(": ", 1)
                if len(parts) == 2:
                    headers[parts[0]] = parts[1]
            headers['code'] = lines[len(lines) - 1]
        return headers

    def sendPacket(self, pktDump):
        assert len(pktDump) < 128
        logging.debug('sendPacket on %s [size=%d]' % (self.clientSocket,
                                                      len(pktDump)))
        
        # 1st byte: fin bit set. text frame bits set.
        # 2nd byte: no mask. length set in 1 byte. 
        resp = bytearray([0b10000001, len(pktDump)])
        # append the data bytes
        for d in bytearray(pktDump):
            resp.append(d)
            
        self.clientSocket.send(resp)
    
    def recvPacket(self):
        logging.debug('recvPacket on %s' % self.clientSocket)
        # as a simple server, we expect to receive:
        #    - all data at one go and one frame
        #    - one frame at a time
        #    - text protocol
        #    - no ping pong messages

        data = bytearray(self.clientSocket.recv(512))
        logging.debug('%d bytes received from %s.' % (len(data), self.clientSocket))
        if len(data) < 6:
            logging.warn('data length too short')
            #raise RemoteDisconnectionError()
            return ''
            #raise Exception("Error reading data - %d bytes received." % len(data))
        # FIN bit must be set to indicate end of frame
        assert(0x1 == (0xFF & data[0]) >> 7)
        # data must be a text frame
        # 0x8 (close connection) is handled with assertion failure
        if 0x1 != (0xF & data[0]):
            logging.warn('not text frame')
            raise RemoteDisconnectionError()
        
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