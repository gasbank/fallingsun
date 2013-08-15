import stackless  # @UnresolvedImport
import random, math

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

    def getRandomLocationAround(self, r):
        
        return (self.location[0] + (2*random.random() - 1) * r,
                self.location[1] + (2*random.random() - 1) * r)

    def getRandomSign(self):
        
        return 2*random.randrange(0,2)-1
        
    def getRandomLocationAround2(self, r0, r1):
        
        return (self.location[0] + self.getRandomSign() * (r0 + random.random() * (r1-r0)),
                self.location[1] + self.getRandomSign() * (r0 + random.random() * (r1-r0)))
    
    def isNear(self, loc):
        
        return self.sqDistanceWithMe(loc) < 25
    
    def sqDistanceWithMe(self, loc):
        
        return sum(((self.location[i] - loc[i])**2 for i in [0,1]))
    
    def getAngleTo(self, loc):
        return math.degrees(math.atan2(-(self.location[0] - loc[0]),
                                       self.location[1] - loc[1]))

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
        