import stackless
import pygame
import math, os, sys, random
from collections import OrderedDict, Counter

random.seed(1)

swidth = 500
sheight = 500
totalWood = 0

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
        
class WorldState:
    def __init__(self, updateRate, time):
        self.updateRate = updateRate
        self.time = time
        self.actors = []

class SWorld(SActor):
    def __init__(self):
        SActor.__init__(self)
        self.registeredActors = OrderedDict()
        #self.registeredActors = {}
        self.maxUpdateRate = 30
        self.updateRate = self.maxUpdateRate
        self.showHavestResult = False
        t = NamedTasklet(self.tick)()
        t.name = "WorldTick"
        #print("World created.")
    
    def getTaskletName(self):
        return "World"
    
    def killDeadActors(self):
        for actor in list(self.registeredActors):
            if self.registeredActors[actor].hitpoints <= 0:
                #print "SWorld --TaskletExit-->", actor
                actor.send_exception(TaskletExit)
                del self.registeredActors[actor]
        
    """            
    def testForCollisions(self, x, y, otherActors=[]):
        collisions = []
        for otherActor, bx, by in otherActors:
            if (x-bx)**2 + (y-by)**2 < 16*16:
                collisions.append(otherActor)
        
        return collisions
    """
    
    def testForCollisions(self, x, y, otherActors=[]):
        collisions = []
        for otherActor, bx, by in otherActors:
            if abs(x-bx) < 16 and  abs(y-by) < 16:
                collisions.append(otherActor)
        
        return collisions
        
    def updateActorPosition(self):
        actorPositions = []
        
        for actor in list(self.registeredActors):
            actorProp = self.registeredActors[actor]
            if actorProp.public:
                x, y = actorProp.location
                angle = actorProp.angle
                velocity = actorProp.velocity
                dx, dy = ( math.sin(math.radians(angle)) * velocity,
                           math.cos(math.radians(angle)) * velocity )
                
                x += dx / self.updateRate
                y -= dy / self.updateRate
                
                collisions = self.testForCollisions(x, y, actorPositions)
                
                for collision in collisions:
                
                    if actor and collision:
                    
                        collisionProp = self.registeredActors[collision]
                    
                        #print self.channel, "--COLLISION-->", actor
                        actor.send((self.channel, "COLLISION", actor, collision, actorProp, collisionProp))
                        if collision and collision is not self.channel:
                            #print self.channel, "--COLLISION-->", collision
                            collision.send((self.channel, "COLLISION", collision, actor, collisionProp, actorProp))
                        pass
                    #else:
                        #actorProp.location = (x, y)
                        
                actorProp.location = (x, y)
                
                actorPositions.append((actor, actorProp.location[0], actorProp.location[1]))
            
    def sendWorldStateToActors(self, startTime):
        ws = WorldState(self.updateRate, startTime)
        for actor in list(self.registeredActors):
            if self.registeredActors[actor].public:
                ws.actors.append((actor, self.registeredActors[actor]))
                
        for actor in list(self.registeredActors):
            #print self.channel, "--WORLD_STATE-->", actor
            actor.send((self.channel, "WORLD_STATE", ws))

    def checkForGatherings(self):
        #print "HAT2!"
        for actor in list(self.registeredActors):
            if self.registeredActors[actor].havestable:
                return
                
        #self.world.send((self.channel, "PRINT_INFO"))
        
        self.channel.send((self.channel, "PRINT_INFO"))
        #print "HAT!"
        
    def tick(self):
        startTime = 0 #time.clock()
        while 1:
            
            self.killDeadActors()
            self.updateActorPosition()
            self.sendWorldStateToActors(startTime)
            self.checkForGatherings()
            if self.showHavestResult:
                self.printHavestResult()
                self.showHavestResult = False
            
            startTime += 1.0 / self.updateRate

            stackless.schedule()
            
        print("Should not see this")
            
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "JOIN":
            self.registeredActors[sentFrom] = msgArgs[0]
        elif msg == "UPDATE_VECTOR":
            self.registeredActors[sentFrom].angle = msgArgs[0]
            self.registeredActors[sentFrom].velocity = msgArgs[1]
        elif msg == "UPDATE_HAVESTABLE":
            self.registeredActors[sentFrom].havestable = msgArgs[0]
        elif msg == "KILLME":
            self.registeredActors[sentFrom].hitpoints = 0
            pass
        elif msg == "PRINT_INFO":
            self.showHavestResult = True
            
        else:
            print("ERROR: The world got unknown message:", msg);
            
    def printHavestResult(self):
        global totalWood
        totalWood = 0
        totalGatherings = []
        for actor in list(self.registeredActors):
            #print self.channel, "--IDENTIFY_HAVEST_RESULT-->", actor
            actor.send((self.channel, "IDENTIFY_HAVEST_RESULT", totalGatherings))
        
        if len(totalGatherings) == 0:
            return
        
        #tg = sum((Counter(dict(x)) for x in totalGatherings), Counter())
        #print tg
        tgStr = ",".join([str(w['WOOD'] if w.has_key('WOOD') else 0) for w in totalGatherings])
        print hex(hash(tgStr)), tgStr
        sys.exit(0)
        

gWorld = SWorld().channel

class SDisplayWindow(SActor):
    def __init__(self, world=gWorld):
        SActor.__init__(self)
        self.world = world
        self.icons = {}
        pygame.init()
        
        self.font = pygame.font.SysFont("monospace", 15)
        
        pygame.display.set_mode((swidth, sheight))
        pygame.display.set_caption("MmoActor")
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         public=False)))
        #print("DisplayWindow created")
    
    def getTaskletName(self):
        return "DisplayWindow"
        
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            #print "Display updated"
            self.updateDisplay(msgArgs)
            pass
            
    def getIcon(self, iconName):
        if self.icons.has_key(iconName):
            return self.icons[iconName]
        else:
            iconFile = os.path.join("data", "%s.bmp" % iconName)
            surface = pygame.image.load(iconFile)
            surface.set_colorkey((0xf3, 0x0a, 0x0a))
            self.icons[iconName] = surface
            return surface
        
    def updateDisplay(self, msgArgs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                print self.channel, "--APP_EXIT-->", self.world
                self.world.send((self.channel, "PRINT_INFO"))
                
        screen = pygame.display.get_surface()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200,200,200))
        screen.blit(background, (0, 0))
        
        ws = msgArgs[0]
        for _, actorProp in ws.actors:
            itemImage = self.getIcon(actorProp.name)
            itemImage = pygame.transform.rotate(itemImage, -actorProp.angle)
            screen.blit(itemImage, actorProp.location)
            
            label = self.font.render(actorProp.name, 1, (255,0,0))
            screen.blit(label, actorProp.location)
            
        pygame.display.flip() 
        
        #print("We have",stackless.runcount,"tasklet(s).")


class SHome(SActor):
    def __init__(self, location=(0,0), world=gWorld, instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.world = world
        self.location = location
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         hitpoints=100)))
    def getTaskletName(self):
        return self.instanceName
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            pass

class STree(SActor):
    def __init__(self, gatheringName, location=(0,0), hitpoints=5, world=gWorld, instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.world = world
        self.hitpoints = hitpoints
        self.havestable = self.hitpoints > 0
        self.havesters = []
        self.gatheringName = gatheringName
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=0,
                                         velocity=0,
                                         height=32,
                                         width=32,
                                         hitpoints=self.hitpoints,
                                         havestable=self.havestable)))
    def getTaskletName(self):
        return self.instanceName
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            pass
        elif msg == "HAVEST":
            
            if self.hitpoints > 0:
                #self.havesters.append(sentFrom)
                self.hitpoints -= 1
                #print self.channel, "--ACQUIRE-->", sentFrom
                sentFrom.send((self.channel, "ACQUIRE", self.gatheringName, 1))
                #print "ACQUIRE_WOOD sent. hitpoints=", self.hitpoints
            
            #print self.channel, "--UPDATE_HAVESTABLE-->", self.world
            self.world.send((self.channel, "UPDATE_HAVESTABLE", self.hitpoints > 0))                
            
            if self.hitpoints <= 0:
                #sentFrom.send((self.channel, "ACQUIRE_WOOD", 0))
                """
                for h in self.havesters:
                    print self.channel, "--DEPLETED-->", h
                    h.send((self.channel, "DEPLETED"))
                self.havesters = [] #None
                """
                #print self.channel, "--KILLME-->", self.world
                self.world.send((self.channel, "KILLME"))
                #print self.channel, "STree DEPLETED and KILLME sent.", self.hitpoints
            
class SWoodcutter(SActor):
    def __init__(self, location=(0,0), angle=135, velocity=0, hitpoints=10, homeLocation=None, world=gWorld, instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.time = 0
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.havestingTask = None
        self.havestTarget = None
        self.havestTargetProp = None
        self.gatherings = OrderedDict()
        self.havestingChannel = stackless.channel()
        self.lastHavestTime = -1
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints)))
    
    def getTaskletName(self):
        return self.instanceName
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
        
            self.time = msgArgs[0].time
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            
            havestables = []
            for actor in msgArgs[0].actors:
                actorProp = actor[1]
                if actorProp.havestable:
                    havestables.append(actor)
            
            if havestables and self.havestTarget is None:
                havestable = random.choice(havestables)
                self.havestTarget = havestable[0]
                self.havestTargetProp = havestable[1]
                
            if self.havestTargetProp and not self.havestTargetProp.havestable:
                self.havestTarget = None
                self.havestTargetProp = None
            #print self.havestTarget, self.havestTargetProp
            """
            for actor in msgArgs[0].actors:
                if actor[1].name == "STree":
                    self.havestTarget = actor[0]
                    havestTargetProp = actor[1]
            """     
            
            if self.havestTargetProp:
                self.angle = math.degrees(math.atan2(-(self.location[0] - self.havestTargetProp.location[0]),
                                                     self.location[1] - self.havestTargetProp.location[1]))
                #self.velocity = 3
            elif self.homeLocation:
                self.angle = math.degrees(math.atan2(-(self.location[0] - self.homeLocation[0]),
                                                     self.location[1] - self.homeLocation[1]))
                #self.velocity = 6
                
            else:
                #self.velocity = 0
                pass
            
            
            
            #self.angle += 10.0 * (1.0 / msgArgs[0].updateRate)
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle, self.velocity)
            self.world.send(updateMsg)
            
        elif msg == "COLLISION":
            # Send a HAVEST message from the woodcutter to the tree. (NOT FROM THE TREE TO THE WOODCUTTER)
            if self.havestingTask is None:
                
                if self.channel is msgArgs[0]:
                    target = msgArgs[1]
                    targetProp = msgArgs[1+2]
                elif self.channel is msgArgs[1]:
                    target = msgArgs[0]
                    targetProp = msgArgs[0+2]
                else:
                    raise RuntimeError("What happened?")
                
                if target is not self.havestTarget:
                    return
                
                #print "Woodcutter channel =",self.channel, "/targetProp.name=", targetProp.name
                
                if targetProp.havestable:
                
                    #print "Woodcutter channel =",self.channel
                    if self.lastHavestTime < 0 or self.time - self.lastHavestTime > 5:
                        #print self.channel, "--HAVEST-->", target, target.balance, target.closed, target.closing
                        target.send((self.channel, "HAVEST"))
                        self.lastHavestTime = self.time
                    
                    
                    #self.havestingTask = stackless.tasklet(self.havestWood)(target)
                    
                #print "COLLISION!!!"
                #self.havestingChannel.send((sentFrom, msg, msgArgs))
                
                
            
        elif msg == "ACQUIRE":
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            if self.gatherings.has_key(gathering):
                self.gatherings[gathering] += gatheringCount
            else:
                self.gatherings[gathering] = gatheringCount

        elif msg == "IDENTIFY_HAVEST_RESULT":
            #print self.channel, self.instanceName, "HAVESTED:", self.gatherings
            global totalWood
            if self.gatherings.has_key("WOOD"):
                totalWood += self.gatherings['WOOD']
            msgArgs[0].append(self.gatherings)
        

SDisplayWindow()        

homeList = []
#gatheringList = [ "WOOD", "APPLE" ]
gatheringList = [ "WOOD" ]

for i in range(1):
    homeList.append(SHome((random.randrange(50,450),random.randrange(50,450)), instanceName="Home #%d" % i))

for i in range(1):
    gatheringName = random.choice(gatheringList)
    STree(gatheringName, (random.randrange(50,450),random.randrange(50,450)), instanceName="Tree #%d [%s]" % (i, gatheringName))

for i in range(1):
    SWoodcutter((random.randrange(50,450),random.randrange(50,450)),
                homeLocation=random.choice(homeList).location,
                velocity=50+(random.random()-0.5)*3,
                instanceName="Woodcutter #%d" % (i+1)
                )

logFile = open('schedlog.log', 'w')                
                
def schedule_cb(prev, next):
    #logFile.write("SCHEDULE %s --> %s\n" % (prev, next))
    logFile.write("%s\n" % next)

#stackless.set_schedule_callback(schedule_cb)
                
try:
    #stackless.run(100000000, totaltimeout=True)
    stackless.run()
    
except KeyboardInterrupt:
    print "Exit"

print "totalWood=", totalWood
