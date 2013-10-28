import socket

s = socket.socket()
s.connect(('127.0.0.1', 3000))

while 1:
    '''
    i = raw_input(s.recv(500))
    s.send(i + '\r\n')
    '''
    print s.recv(500),
