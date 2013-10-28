from twisted.internet import reactor
from twisted.web.websocket import WebSocketHandler, WebSocketSite
from twisted.web.static import File

class Echohandler(WebSocketHandler):
    def frameReceived(self, frame):
        self.transport.write(frame)
        
if __name__ == '__main__':
    root = File('.')
    site = WebSocketSite(root)
    site.addHandler('/echo', Echohandler)
    reactor.listenTCP(8080, site)
    reactor.run()
