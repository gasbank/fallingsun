import stackless  # @UnresolvedImport
import random
import math
import logging

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
        return self.__repr__()
    def __repr__(self):
        assert(len(self.name) > 0)
        return "<Tasklet(%s) 0x%08X>" % (self.name, id(self))
    
class NamedChannel(stackless.channel):
    name = ''
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        assert(len(self.name) > 0)
        return "<Channel(%s) 0x%08X>" % (self.name, id(self))
        
class SActor(object):
    @property
    def instanceName(self):
        return self._instanceName
    
    @property
    def neighbors(self):
        return self._neighbors
    
    def __init__(self, instanceName='', display=None):
        self._instanceName = instanceName
        self._display = display
        self._neighbors = set()
        
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
    
    # Squared-distance with me
    def sqDistanceWithMe(self, loc):
        
        return sum(((self.location[i] - loc[i])**2 for i in [0,1]))
    
    # Manhattan-distance with me
    def manDistanceWithMe(self, loc):
        
        return sum(abs(self.location[i] - loc[i]) for i in [0,1])
    
    def getAngleTo(self, loc):
        return math.degrees(math.atan2(-(self.location[0] - loc[0]),
                                       self.location[1] - loc[1]))

    def findNewRoamingPathWithin(self, t, tileData):
        
        path = None
        tryCount = 0
        while not path:
            
            tryCount += 1
            
            assert tryCount < 100
        
            goalTile = self.getRandomTileAround(t)
            
            if not tileData.isMovable(int(goalTile[0]//32), int(goalTile[1]//32)):
                stackless.schedule()
                continue
            
            path = tileData.findPath(self.getTileLocation()[0],
                                     self.getTileLocation()[1],
                                     int(goalTile[0]//32),
                                     int(goalTile[1]//32))

        return path
    
    def getLocationFromTile(self, tileIndex):
        return (tileIndex[0]*32+16, tileIndex[1]*32+16)
    
    def getTileLocation(self):
        return (int(self.location[0]//32), int(self.location[1]//32))
    
    def info(self, msg):
        logging.info('%s:%s' % (self.instanceName, msg))
        
    def debug(self, msg):
        logging.debug('%s:%s' % (self.instanceName, msg))
        
    def sendDisplay(self, msg):
        if self._display:
            self._display.send(msg)
    
class ActorProperties:
    def __init__(self, name, location=(-1,-1), angle=0, velocity=0, height=-1,
                 width=-1, hitpoints=1, public=True, harvestable=False,
                 physical=True, animatedSprite=False, instanceName='',
                 tickEvent=True, staticSprite=False):
        
        self.name = name
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.height = height
        self.width = width
        self.hitpoints = hitpoints
        self.public = public
        self.harvestable = harvestable
        self.physical = physical
        self.animatedSprite = animatedSprite
        self.instanceName = instanceName
        self.tickEvent = tickEvent
        self.intention = ''
        self.staticSprite = staticSprite
        self.waitGauge = None
        self.neighbors = set()
      