import stackless  # @UnresolvedImport
from actor import SActor, NamedTasklet
from collections import OrderedDict
import math, logging
from tree import STree
import random
from home import SHome
import level
import time

class WorldState:
    def __init__(self, updateRate, time, tileData):
        self.updateRate = updateRate
        self.time = time
        self.actors = []
        self.tileData = tileData
        
        
class SWorld(SActor):
    def __init__(self, spawnTreeInterval=0, exitOnNoHavestables=False,
                 disableCollisionCheck=False):
        SActor.__init__(self)
        
        self.registeredActors = OrderedDict()
        self.aboutToBeKilledActors = OrderedDict()
        self.tickDisabledActors = OrderedDict()
        
        self.maxUpdateRate = 30
        self.updateRate = self.maxUpdateRate
        self.showHavestResult = False
        self.spawnTreeInterval = spawnTreeInterval
        self.exitOnNoHavestables = exitOnNoHavestables
        self.lastSpawnTreeTime = -1
        self.tickTasklet = None
        self.tickLoopEnable = True
        self.disableCollisionCheck = disableCollisionCheck
        self.tileData = level.TileLevel(15, 15)
        
        logging.info('The world created.')
    
    def getTaskletName(self):
        return "World"
    
    def startTickTasklet(self):
        assert self.tickTasklet == None
        
        self.tickTasklet = NamedTasklet(self.tickLoop)()
        self.tickTasklet.name = 'WorldTick'
        self.tickLoopEnable = True
        
    def killDeadActors(self):
        
        for actor in self.aboutToBeKilledActors:
            actor.send((self.channel, 'YOU_ARE_DEAD'))
            actor.send_exception(TaskletExit)
            del self.registeredActors[actor]
        
        self.aboutToBeKilledActors.clear()
        
        '''
        for actor in list(self.registeredActors):
            if self.registeredActors[actor].hitpoints <= 0:
                #print "SWorld --TaskletExit-->", actor
                actor.send((self.channel, 'YOU_ARE_DEAD'))
                actor.send_exception(TaskletExit)
                del self.registeredActors[actor]
                '''

    def testForCollisions(self, x, y, otherActors=[]):
        collisions = []
        for otherActor, bx, by in otherActors:
            if abs(x-bx) < 16 and  abs(y-by) < 16:
                collisions.append(otherActor)
        
        return collisions
    
    def collisionCheck(self, x, y, actor, actorProp, actorPositions):
    
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
            #    actorProp.location = (x, y)
        
        #if not collisions:        
        #    actorProp.location = (x, y)
                
        
    def updateActorPosition(self):
        actorPositions = []
        
        for actor in self.registeredActors:
            actorProp = self.registeredActors[actor]
            if actorProp.public:
                x, y = actorProp.location
                angle = actorProp.angle
                velocity = actorProp.velocity
                dx, dy = ( math.sin(math.radians(angle)) * velocity,
                           math.cos(math.radians(angle)) * velocity )
                
                x += dx / self.updateRate
                y -= dy / self.updateRate
                
                if not self.disableCollisionCheck:
                    self.collisionCheck(x, y, actor, actorProp, actorPositions)
                
                actorProp.location = (x, y)
                actorPositions.append((actor, 
                                       actorProp.location[0], 
                                       actorProp.location[1]))
            
    def sendWorldStateToActors(self, startTime):
        ws = WorldState(self.updateRate, startTime, self.tileData)
        for actor in self.registeredActors:
            if self.registeredActors[actor].public:
                ws.actors.append((actor, self.registeredActors[actor]))
                
        for actor in self.registeredActors:
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
            STree(self.channel, "WOOD",
                  (random.randrange(50,450),
                   random.randrange(50,450)),
                  instanceName="SpawnedTree")
        
    def updateTickDisabledActors(self):
        # Move tick-disabled actors from 'self.registeredActors'
        # to 'self.tickDisabledActors'.
        
        for actor in list(self.registeredActors):
            if not self.registeredActors[actor].tickEvent:
                self.tickDisabledActors[actor] = self.registeredActors[actor]
                del self.registeredActors[actor]

    def processOneTick(self, startTime):
        # The whole thing that happens during a tick!
        
        self.updateTickDisabledActors()
        self.killDeadActors()
        self.updateActorPosition()
        self.sendWorldStateToActors(startTime)

        if 0 < self.spawnTreeInterval < startTime - self.lastSpawnTreeTime:
            self.spawnTree()
            self.lastSpawnTreeTime = startTime
        
        if self.showHavestResult:
            self.printHavestResult()
            self.showHavestResult = False
            
        if self.exitOnNoHavestables:
            havestables = self.getHavestables()
            if not havestables:
                self.tickLoopEnable = False

        if not self.registeredActors and not self.aboutToBeKilledActors and not self.tickDisabledActors:
            self.tickLoopEnable = False
        
    def tickLoop(self):
        startTime = 0 #time.clock()
        while self.tickLoopEnable:
            
            self.processOneTick(startTime)
                        
            startTime += 1.0 / self.updateRate
            
            stackless.schedule()
            
        print("The world tick loop about to exit...")
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'JOIN':
            self.registeredActors[sentFrom] = msgArgs[0]
        elif msg == 'UPDATE_VECTOR':
            self.registeredActors[sentFrom].angle = msgArgs[0]
            self.registeredActors[sentFrom].velocity = msgArgs[1]
        elif msg == 'UPDATE_HAVESTABLE':
            self.registeredActors[sentFrom].havestable = msgArgs[0]                
        elif msg == 'UPDATE_INTENTION':
            self.registeredActors[sentFrom].intention = msgArgs[0]
        elif msg == 'UPDATE_MY_HP':
            self.registeredActors[sentFrom].hitpoints = msgArgs[0]
            if msgArgs[0] == 0:
                self.aboutToBeKilledActors[sentFrom] = self.registeredActors[sentFrom]
        elif msg == 'KILLME':
            self.registeredActors[sentFrom].hitpoints = 0
            self.aboutToBeKilledActors[sentFrom] = self.registeredActors[sentFrom]
        elif msg == 'PRINT_INFO':
            self.showHavestResult = True
        elif msg == 'SPAWN_HOME':
            SHome(self.channel, location=msgArgs[0], instanceName="Architect Home")
        elif msg == 'START_TICK_TASKLET':
            self.startTickTasklet()
        elif msg == 'STOP_TICK_LOOP':
            self.tickLoopEnable = False
        elif msg == 'NO_MORE_TICK_EVENT':
            self.registeredActors[sentFrom].tickEvent = False
        else:
            raise RuntimeError("ERROR: The world got unknown message: %s" % msg);
            
    def printHavestResult(self):
        global totalWood
        totalWood = 0
        totalGatherings = []
        for actor in list(self.registeredActors):
            #print self.channel, "--IDENTIFY_HAVEST_RESULT-->", actor
            actor.send((self.channel, "IDENTIFY_HAVEST_RESULT", totalGatherings))

        tgStr = ",".join([str(w['WOOD'] if w.has_key('WOOD') else 0) for w in totalGatherings])
        print hex(hash(tgStr)), tgStr
        
    def killAll(self):
        for actor in list(self.registeredActors):
            actor.send_exception(TaskletExit)
            
    def getHavestables(self):
        return [k for k,v in self.registeredActors.items() if v.havestable]
            