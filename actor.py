import stackless  # @UnresolvedImport
import random, math

gTasklets = []
gChannels = []

def printAllActorChannelBalances():
    for c in gChannels:
        print c, (c, c.balance)
        while c.balance > 0:
            print '   ', c.receive()
            
    for t in gTasklets:
        print t, t.alive, t.paused, t.blocked, t.scheduled, t.restorable

class NamedTasklet(stackless.tasklet):
    name = ""

    def __str__(self):
        assert(len(self.name) > 0)
        return "<NamedTasklet(name='%s')>" % self.name

class NamedChannel(stackless.channel):
    name = ''
    
    def __str__(self):
        assert(len(self.name) > 0)
        return "<NamedChannel(name='%s')>" % self.name
        
class SActor:
    def __init__(self, instanceName=''):
        self.instanceName = instanceName
        
        self.channel = NamedChannel()
        self.channel.name = self.getTaskletName() + 'Channel'
        
        global gChannels
        gChannels.append(self.channel)
        
        self.processMessageMethod = self.defaultMessageAction
        t = NamedTasklet(self.processMessage)()
        t.name = self.getTaskletName()
        
        global gTasklets
        gTasklets.append(t)

    def getTaskletName(self):
        return self.instanceName
    
    def processMessage(self):
        while 1:
            self.processMessageMethod(self.channel.receive())
            
    def defaultMessageAction(self, args):
        pass
        
    def getRandomTileAround(self, t):
        
        v = (self.location[0] // 32 * 32 + (2*random.random() - 1) * 32 * t,
             self.location[1] // 32 * 32 + (2*random.random() - 1) * 32 * t)
        
        return (max(32*1, min(v[0], 32*10)),
                max(32*1, min(v[1], 32*10)))

    def getRandomLocationAround(self, r):
        
        v = (self.location[0] + (2*random.random() - 1) * r,
             self.location[1] + (2*random.random() - 1) * r)
        
        return (max(50, min(v[0], 450)),
                max(50, min(v[1], 450)))
        
    def getRandomSign(self):
        
        return 2*random.randrange(0,2)-1
        
    def getRandomLocationAround2(self, r0, r1):
        
        v = (self.location[0] + self.getRandomSign() * (r0 + random.random() * (r1-r0)),
             self.location[1] + self.getRandomSign() * (r0 + random.random() * (r1-r0)))
        
        return (max(50, min(v[0], 450)),
                max(50, min(v[1], 450)))
    
    def isNear(self, loc, threshold = 25):
        
        return self.sqDistanceWithMe(loc) < threshold
    
    def sqDistanceWithMe(self, loc):
        
        return sum(((self.location[i] - loc[i])**2 for i in [0,1]))
    
    def getAngleTo(self, loc):
        return math.degrees(math.atan2(-(self.location[0] - loc[0]),
                                       self.location[1] - loc[1]))

class ActorProperties:
    def __init__(self, name, location=(-1,-1), angle=0, velocity=0, height=-1,
                 width=-1, hitpoints=1, public=True, havestable=False,
                 physical=True, animatedSprite=False):
        
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
        self.animatedSprite = animatedSprite
        