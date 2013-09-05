import stackless  # @UnresolvedImport
from actor import SActor, NamedTasklet
from collections import OrderedDict
import math
from tree import STree
import random
from home import SHome
import level
import weakref
import time
import kdtree

class WorldState:
    def __init__(self, updateRate, time, tileData):
        self.updateRate = updateRate
        self.time = time
        self.actors = []
        self.actorsDict = {}
        self.tileData = tileData

class KdActorNode(kdtree.KdNode): pass        
        
class SWorld(SActor):
    def __init__(self, spawnTreeInterval=0, exitOnNoHarvestables=False,
                 disableCollisionCheck=False, width=10, height=10,
                 useTestData=False):
        
        SActor.__init__(self, 'World')
        
        # Actor dictionaries
        self.registeredActors = {}
        self.kdActorTree = kdtree.KdTree(searchSpace=kdtree.Rect(0,0,10**9,10**9))
        self.aboutToBeKilledActors = {}
        self.tickDisabledActors = {}
        #self.sightActors = weakref.WeakValueDictionary() #{}
        
        
        # Tick
        self.maxUpdateRate = 30
        self.updateRate = self.maxUpdateRate
        self.tickTasklet = None
        self.tickLoopEnable = True
        self.tickOnlyOnce = False

        # Level
        self.tileData = level.TileLevel(width, height, useTestData=useTestData)
        
        self.showHarvestResult = False
        self.spawnTreeInterval = spawnTreeInterval
        self.exitOnNoHarvestables = exitOnNoHarvestables
        self.lastSpawnTreeTime = -1
        self.disableCollisionCheck = disableCollisionCheck
        
        # Network
        self._server = None
        self._client = None
        
        self.debug('Created.')
    
    def startTickTasklet(self, tickOnlyOnce=False):
        assert self.tickTasklet == None
        
        self.tickLoopEnable = True
        self.tickOnlyOnce = tickOnlyOnce
        
        self.tickTasklet = NamedTasklet(self.tickLoop)()
        self.tickTasklet.name = 'WorldTick'
                
    def killDeadActors(self):
        
        for actor in list(self.aboutToBeKilledActors):
            actor.send((self.channel, 'YOU_ARE_DEAD'))
            actor.send_exception(TaskletExit)
            
            if self.registeredActors[actor].staticSprite:
                
                if self.registeredActors[actor].name == 'STree':
                    
                    self.tileData.placeTree(int(self.registeredActors[actor].location[0]//32),
                                            int(self.registeredActors[actor].location[1]//32),
                                            False)
                    
                elif self.registeredActors[actor].name == 'SHome':
                    
                    self.tileData.placeTent(int(self.registeredActors[actor].location[0]//32),
                                            int(self.registeredActors[actor].location[1]//32),
                                            False)
            
            self.info('%s about to be destroyed.' % self.registeredActors[actor].instanceName)
            del self.registeredActors[actor]
        
        self.aboutToBeKilledActors.clear()
        
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
                ws.actorsDict[actor] = self.registeredActors[actor]
        
        for actor, prop in self.registeredActors.iteritems():
            self.debug('%s --WORLD_STATE--> %s' % (self.channel, actor))
            actor.send((self.channel, "WORLD_STATE", ws, prop))
        

    def checkForGatherings(self):
        #print "HAT2!"
        for actor in list(self.registeredActors):
            if self.registeredActors[actor].harvestable:
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

    def sendSightNeighborEnterLeaveToActors(self):
        
        for p in self.registeredActors.itervalues():
            p.neighbored.clear()
        
        for a, p in self.registeredActors.iteritems():
            if p.name != 'SSight': continue

            oldNeighbors = p.neighbors
            p.neighbors = set()
            
            k = self.tileData.toTileIndex(p.location)
            
            for aa, pp in self.registeredActors.iteritems():
                if a is aa: continue
                
                kk = self.tileData.toTileIndex(pp.location)
                
                isNeighbor = None
                if p.name is 'SSight':
                    isNeighbor = (abs(k[0] - kk[0]) <= p.sightRange) and (abs(k[1] - kk[1]) <= p.sightRange) 
                else:
                    isNeighbor = abs(k[0] - kk[0]) + abs(k[1] - kk[1]) <= 1
                
                if isNeighbor:
                    p.neighbors.add((weakref.ref(aa), weakref.ref(pp)))
                    pp.neighbored.add((weakref.ref(a), weakref.ref(p)))
                    
            newlyLeft = oldNeighbors - p.neighbors
            newlyEntered = p.neighbors - oldNeighbors
            
            if newlyLeft:
                a.send((self.channel, 'NEIGHBORS_LEFT', newlyLeft))
            if newlyEntered:
                a.send((self.channel, 'NEIGHBORS_ENTERED', newlyEntered))

    def sendNeighborEnterLeaveToActors(self):
        
        for p in self.registeredActors.itervalues():
            p.neighbored.clear()
        
        for a, p in self.registeredActors.iteritems():
            if not p.public: continue
            
            oldNeighbors = p.neighbors
            p.neighbors = set()
            
            k = self.tileData.toTileIndex(p.location)
            
            for aa, pp in self.registeredActors.iteritems():
                if a is aa: continue
                
                kk = self.tileData.toTileIndex(pp.location)
                
                isNeighbor = None
                if p.name is 'SSight':
                    isNeighbor = (abs(k[0] - kk[0]) <= p.sightRange) and (abs(k[1] - kk[1]) <= p.sightRange) 
                else:
                    isNeighbor = abs(k[0] - kk[0]) + abs(k[1] - kk[1]) <= 1
                
                if isNeighbor:
                    p.neighbors.add((weakref.ref(aa), weakref.ref(pp)))
                    pp.neighbored.add((weakref.ref(a), weakref.ref(p)))
                    
            newlyLeft = oldNeighbors - p.neighbors
            newlyEntered = p.neighbors - oldNeighbors
            
            if newlyLeft:
                a.send((self.channel, 'NEIGHBORS_LEFT', newlyLeft))
            if newlyEntered:
                a.send((self.channel, 'NEIGHBORS_ENTERED', newlyEntered))
        
    
    def processOneTick(self, startTime):
        # The whole thing that happens during a tick!
        
        self.updateTickDisabledActors()
        self.killDeadActors()
        self.updateActorPosition()
        self.sendWorldStateToActors(startTime)
        #self.sendNeighborEnterLeaveToActors()
        #self.sendSightNeighborEnterLeaveToActors()

        if 0 < self.spawnTreeInterval < startTime - self.lastSpawnTreeTime:
            self.spawnTree()
            self.lastSpawnTreeTime = startTime
        
        if self.showHarvestResult:
            self.printHarvestResult()
            self.showHarvestResult = False
            
        if self.exitOnNoHarvestables:
            harvestables = self.getharvestables()
            if not harvestables:
                self.tickLoopEnable = False

        if not self.registeredActors and not self.aboutToBeKilledActors and not self.tickDisabledActors:
            self.tickLoopEnable = False
            
    def tickLoop(self):
        startTime = 0 #time.clock()
        while self.tickLoopEnable:
            curClock = time.clock()
            
            self.processOneTick(startTime)
            
            #self.info('Tick took %.3f seconds.' % (time.clock() - curClock))
                        
            startTime += 1.0 / self.updateRate
            
            if self.tickOnlyOnce:
                self.tickOnlyOnce = False
                self.tickTasklet = None
                break
            
            stackless.schedule()
            
        self.info('The world tick loop about to exit...')
        

    def handleJoin(self, actor, prop):
        self.registeredActors[actor] = prop
            
        if prop.staticSprite:
            
            if prop.name == 'STree':
                
                self.tileData.placeTree(*prop.tileLoc)
                
            elif prop.name == 'SHome':
                
                self.tileData.placeTent(*prop.tileLoc)
        
        '''
        if msgArgs[0].name == 'SSight':
            self.sightActors[id(sentFrom)] = sentFrom
        '''
                
        if prop.name == 'SClient':
            if self._client:
                raise RuntimeError('Second SClient try to join.')
            self._client = actor
        
        if prop.name == 'SServer':
            if self._server:
                raise RuntimeError('Second SServer try to join.')
            self._server = actor

        if prop.public and prop.physical:
            #print actor, prop.location
            node = KdActorNode(prop.location + (weakref.ref(actor),))
            self.kdActorTree.insertNode(node)
        
        self.info('%s joined the world.' % prop.instanceName)
    
    
    def handleQueryRectRange(self, sentFrom, cenLoc, r):
        
        if cenLoc is None:
            cenLoc = self.registeredActors[sentFrom].location
        
        #self.info('QUERY_RANGE_RECT detected.')
        Q = kdtree.Range(cenLoc[0]-r*32, cenLoc[1]-r*32, 32*(2*r+1), 32*(2*r+1))
        points = self.kdActorTree.rangePoints(Q)
        #self.info('QUERY_RESULT about to send...')
        sentFrom.send((self.channel, 'QUERY_RESULT', points))
        #self.info('QUERY_RESULT sent!')
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'JOIN':
            self.handleJoin(sentFrom, msgArgs[0])
            
        elif msg == 'UPDATE_VECTOR':
            oldAngle = self.registeredActors[sentFrom].angle
            oldVelocity = self.registeredActors[sentFrom].velocity
            
            if abs(oldAngle - msgArgs[0]) > 5 or abs(oldVelocity - msgArgs[1]) > 1: 
                self.registeredActors[sentFrom].angle = msgArgs[0]
                self.registeredActors[sentFrom].velocity = msgArgs[1]
                
                for a,p in list(self.registeredActors[sentFrom].neighbored):
                    if a() and p() and p().name == 'SSight':
                        a().send((self.channel, 'UPDATE_VECTOR_OF_NEIGHBORS',
                                (sentFrom, self.registeredActors[sentFrom])))
             
        elif msg == 'UPDATE_HARVESTABLE':
            self.registeredActors[sentFrom].harvestable = msgArgs[0]                
        elif msg == 'UPDATE_INTENTION':
            self.registeredActors[sentFrom].intention = msgArgs[0]
        elif msg == 'UPDATE_MY_HP':
            self.registeredActors[sentFrom].hitpoints = msgArgs[0]
            if msgArgs[0] <= 0:
                self.aboutToBeKilledActors[sentFrom] = self.registeredActors[sentFrom]
        elif msg == 'UPDATE_MY_STAMINA':
            self.registeredActors[sentFrom].stamina = msgArgs[0]
        elif msg == 'UPDATE_MY_WAIT_GAUGE':
            self.registeredActors[sentFrom].waitGauge = msgArgs[0]
        elif msg == 'KILLME':
            self.registeredActors[sentFrom].hitpoints = 0
            self.aboutToBeKilledActors[sentFrom] = self.registeredActors[sentFrom]
        elif msg == 'PRINT_INFO':
            self.showHarvestResult = True
        elif msg == 'SPAWN_HOME':
            SHome(self.channel, location=msgArgs[0], instanceName="Architect Home")
        elif msg == 'START_TICK_TASKLET':
            self.startTickTasklet()
        elif msg == 'START_SINGLE_TICK_TASKLET':
            self.startTickTasklet(tickOnlyOnce=True)
        elif msg == 'STOP_TICK_LOOP':
            self.tickLoopEnable = False
        elif msg == 'CLOSE_WINDOW':
            self.tickLoopEnable = False
            for a,p in self.registeredActors.iteritems():
                if p.name in ['SServer', 'SWebSocketServer', 'SClient']:
                    a.send((self.channel, 'CLOSE_SOCKET'))
        elif msg == 'NO_MORE_TICK_EVENT':
            self.registeredActors[sentFrom].tickEvent = False
        elif msg == 'TELL_ME_WORLD_SIZE':
            sentFrom.send((self.channel, "WORLD_SIZE", self.tileData.width,
                                                       self.tileData.height))
        elif msg == 'SIGHT_RANGE':
            self.registeredActors[sentFrom].sightRange = msgArgs[0]
        elif msg == 'CHAT_TO_ALL':
            for a,p in self.registeredActors.iteritems():
                if p.name == 'SUser':
                    self.debug('%s sent chat message %s to %s.' % (sentFrom,a,msgArgs[0]))
                    a.send((sentFrom, 'CHAT', msgArgs[0]))
        elif msg == 'REQUEST_TELEPORT':
            self.teleportActor(sentFrom, msgArgs[0])
        elif msg == 'REQUEST_RELATIVE_TELEPORT':
            self.relativeTeleportActor(sentFrom, msgArgs[0])
        elif msg == 'QUERY_RECT_RANGE':
            self.handleQueryRectRange(sentFrom, *msgArgs)
        else:
            raise RuntimeError("ERROR: The world got unknown message %s sent from %s"
                               % (msg, sentFrom));
            
    def printHarvestResult(self):
        global totalWood
        totalWood = 0
        totalGatherings = []
        for actor in list(self.registeredActors):
            #print self.channel, "--IDENTIFY_HARVEST_RESULT-->", actor
            actor.send((self.channel, "IDENTIFY_HARVEST_RESULT", totalGatherings))

        tgStr = ",".join([str(w['WOOD'] if w.has_key('WOOD') else 0) for w in totalGatherings])
        print hex(hash(tgStr)), tgStr
        
    def killAll(self):
        for actor in list(self.registeredActors):
            actor.send_exception(TaskletExit)
            
    def getharvestables(self):
        return [k for k,v in self.registeredActors.items() if v.harvestable]
    
    def teleportActor(self, actor, location):
        self.registeredActors[actor].location = location
        
    def relativeTeleportActor(self, actor, dLoc):
        #self.info('REQUEST_RELATIVE_TELEPORT detected.')
        loc = self.registeredActors[actor].location
        newLoc = (loc[0] + dLoc[0], loc[1] + dLoc[1])
        self.registeredActors[actor].location = newLoc
        #self.info('TELEPORTED about to send...')
        actor.send((self.channel, 'TELEPORTED', newLoc))
        #self.info('TELEPORTED sent!')