import stackless

class NamedTasklet(stackless.tasklet):
    name = ""

    def __str__(self):
        assert(len(self.name) > 0)
        return "<NamedTasklet(name='%s')>" % self.name
        
class SActor:
    def __init__(self):
        self.channel = stackless.channel()
        self.processMessageMethod = self.defaultMessageAction
        t = NamedTasklet(self.processMessage)()
        t.name = self.getTaskletName()
        #print("Actor created.")
        #print("We have",stackless.runcount,"tasklet(s) so far.")
        
    def processMessage(self):
        while 1:
            self.processMessageMethod(self.channel.receive())
            
    def defaultMessageAction(self, args):
        pass
        
    def getTaskletName(self):
        return ""
        
class ActorProperties:
    def __init__(self, name, location=(-1,-1), angle=0, velocity=0, height=-1, width=-1, hitpoints=1, public=True, havestable=False, physical=True):
        self.name = name
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.height = height
        self.width = width
        self.hitpoints = hitpoints
        self.public = public
        self.havestable = havestable
        self.physical = physical
        