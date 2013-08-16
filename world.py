import stackless  # @UnresolvedImport
from actor import SActor, NamedTasklet
from collections import OrderedDict, Counter
import math, sys
from tree import STree
import random
from home import SHome

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
        
    def spawnTree(self):
        if random.randrange(0, 10000) < 1:
            STree(self.channel, "WOOD", (random.randrange(50,450),random.randrange(50,450)), instanceName="SpawnedTree")
        
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
            
            self.spawnTree()

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
        elif msg == "UPDATE_MY_HP":
            self.registeredActors[sentFrom].hitpoints = msgArgs[0]
        elif msg == 'SPAWN_HOME':
            SHome(self.channel, location=msgArgs[0], instanceName="Architect Home")
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
        