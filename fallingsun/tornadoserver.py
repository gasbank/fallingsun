# coding: utf-8
import stackless
import tornado.ioloop
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
 
class WSHandler(tornado.websocket.WebSocketHandler):
    waiters=set()
    
    def open(self):
        WSHandler.waiters.add(self)
        
        print 'new connection'
        self.write_message(u"한글 메시지를 봅시다? Hello World~~\n")
        self.write_message("I am the ws server.\n")
      
    def on_message(self, message):
        if message:
            print 'message received %s' % message
            for w in WSHandler.waiters:
                w.write_message('%d: %s\n' % (id(self), message))
 
    def on_close(self):
        print 'connection closed'
      
application = tornado.web.Application([
    (r"/", MainHandler),
    (r'/ws', WSHandler),
])

def myTasklet():
    print 'hehe'

if __name__ == "__main__":
    
    application.listen(8888)
    tInstance = tornado.ioloop.IOLoop.instance()
    print dir(tInstance)
    stackless.tasklet(tInstance.start)()
    stackless.tasklet(myTasklet)()
    stackless.run()
