# coding=utf-8
import random
import weakref
from collections import OrderedDict
from actor import SActor, ActorProperties
from level import TileNeighborhood4
import kdtree

class SWoodcutter(SActor):
    
    @property
    def intention(self):
        return self._intention
    @intention.setter
    def intention(self, value):
        
        if value == self.intention:
            raise RuntimeError('Duplicated intention change call.')
        
        self.waitGauge = None
        self.roamingPath = None
        self.harvestTarget = self.harvestTargetProp = None
        self.pathFindingTarget = None
        
        if value == 'ROAMING':
            self.velocity = 10
        elif value == 'RESTING':
            self.velocity = 0
            self.restFor = 6 + random.random() * 6
        elif value in ['PATHFINDING_HOME', 'PATHFINDING_HARVESTABLE']:
            self.velocity = 50
            pass
        elif value == 'HARVESTING':
            self.velocity = 0
        elif value == 'STOCK_UP_ALL_HARVESTABLES':
            self.velocity = 0
        else:
            raise RuntimeError('%s: Unknown intention %s' % (self, value))

        self.info("intention: %s -> %s" % (self._intention, value))
        self._lastIntentionTime = self.time
        self._intention = value
        
        self.world.send((self.channel, 'UPDATE_INTENTION', self._intention))
        
    @property
    def waitGauge(self):
        return self._waitGauge
    @property
    def waitFinished(self):
        return self._waitGauge <= 0
    @waitGauge.setter
    def waitGauge(self, value):
        self._waitGauge = value
        self.world.send((self.channel, "UPDATE_MY_WAIT_GAUGE", self._waitGauge))
    
    @property
    def stamina(self): return self._stamina
    @stamina.setter
    def stamina(self, value):
        self._stamina = max(0, min(value, self.maxStamina))
    @property
    def staminaFull(self):
        return self.stamina >= self.maxStamina
    @property
    def staminaDepleted(self):
        return self.stamina <= 0
    
    @property
    def maxGatheringsReached(self):
        return sum(self.gatherings.itervalues()) >= self.maxGatherings

    @property
    def hitpoints(self):
        return self._hitpoints
    @property
    def dead(self):
        return self._hitpoints <= 0
    @hitpoints.setter    
    def hitpoints(self, value):
        old = self._hitpoints
        self._hitpoints = value
        if old != self._hitpoints: 
            self.world.send((self.channel, "UPDATE_MY_HP", self._hitpoints))
            self.drawFadeoutText('%s%+d' % ('HP', self._hitpoints - old))
        
    def __init__(self, world, location=(0,0), angle=135, velocity=0,
                 hitpoints=10, homeLocation=None, instanceName="",
                 stamina=5, maxStamina=7, roamingRadius=100,
                 intention='RESTING', home=None, display=None,
                 maxGatherings=2):
        
        SActor.__init__(self, instanceName, display)
        self.time = 0
        self.deltaTime = 0
        self.angle = angle
        self.velocity = velocity
        self._hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.harvestTarget = None
        self.harvestTargetProp = None
        self.gatherings = OrderedDict()
        self.lastHarvestTime = -1
        self.maxStamina = maxStamina
        self._stamina = None
        self.stamina = stamina
        self.roamingTarget = None
        self.lastRoamingTargetTime = None
        self.roamingRadius = roamingRadius
        self.roamingPath = None
        self._lastIntentionTime = -1
        self._intention = None
        self._waitGauge = None
        self.home = weakref.ref(home) if home else None
        self.maxGatherings = maxGatherings
        self._starvationWaitGauge = None
        
        self.debug('Created.')
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         animatedSprite=True,
                                         instanceName=self.instanceName)))
        
        self.intention = intention
    
    def isNeighborTiles(self, tileData, location):
        
        for ni, nj in TileNeighborhood4(tileData.width,
                                        tileData.height,
                                        self.getTileLocation()[0],
                                        self.getTileLocation()[1]):
            if (ni, nj) == (int(location[0]//32), int(location[1]//32)):
                return True
             
        return False
    
    
    def findNeighborHarvestable(self, tileData, actors):
        harvestables = [h for h in actors if h[1].harvestable
                       and h[1].hitpoints > 0
                       and self.isNeighborTiles(tileData, h[1].location)]
    
        if harvestables:
            return min(harvestables, key=lambda h: self.manDistanceWithMe(h[1].location))
        
        return None
    
    def isMyHomeNeighbor(self, ws):
        
        cenLoc = self.location
        r = 1.5
        Q = kdtree.Range(cenLoc[0]-r*32, cenLoc[1]-r*32, 32*(2*r+1), 32*(2*r+1))
        
        for _, _, a in ws.kdActorTree.rangePoints(Q):
            if a is self.home:
                return True
    
        return False
    
    def findClosestHarvestable(self, tileData, actors):
        harvestables = [h for h in actors if h[1].harvestable
                       and h[1].hitpoints > 0]
    
        if harvestables:
            return min(harvestables, key=lambda h: self.manDistanceWithMe(h[1].location))
        
        return None, None
    
    def doPathFindingPixelCoord(self, tileData, nextIntention, x, y):
        self.doPathFinding(tileData, int(x//32), int(y//32), nextIntention)

    def doPathFinding(self, tileData, tileX, tileY, nextIntention):
                
        # If I don't have a roaming path, find for a new one.
        if self.roamingPath is None:
            self.roamingPath = tileData.findPath(self.getTileLocation()[0],
                                                 self.getTileLocation()[1],
                                                 tileX, tileY)
            #print self.roamingPath
            
        # Or check if I am near the current roaming target
        # location.
        elif self.roamingPath and self.isNear(self.getLocationFromTile(self.roamingPath[0]), 9):
             
            # If near, remove the current target location
            self.roamingPath.pop(0)
            
        # Update my angle and velocity if the roaming path available.
        if self.roamingPath:
            
            angle = self.getLocationFromTile(self.roamingPath[0])
            self.angle = self.getAngleTo(angle)
                            
        # Path finding finished.
        else:
            self.intention = nextIntention
    
    
    
    def doHarvesting(self, tileData, actors):
        HARVEST_WAIT_COST = 50
        
        if self.maxGatheringsReached:
            self.intention = 'PATHFINDING_HOME'
            return
                    
        # I'm near the harvestables but don't have any target.
        # Let's find a new target.
        if not self.harvestTarget:
            h = self.findNeighborHarvestable(tileData, actors)
            if h:
                
                self.angle = self.getAngleTo(h[1].location)
                
                #print h, h[1].instanceName, self.angle
                
                self.harvestTarget = h[0]
                self.harvestTargetProp = h[1]
                self.waitGauge = HARVEST_WAIT_COST
        
        # If we have a valid target then subtract some wait gauge.
        if self.harvestTarget and self.harvestTargetProp.harvestable:
            if self.waitGauge <= 0:
                self.waitGauge = HARVEST_WAIT_COST
            else:
                self.waitGauge -= 0.25
            
            if self.waitFinished:
            
                self.info('--%s--> %s' % ('HARVEST',
                                          self.harvestTargetProp.instanceName))
                self.harvestTarget.send((self.channel, "HARVEST"))
                
                # Refill the wait gauge.
                #self.waitGauge = HARVEST_WAIT_COST
        
        else:
            if self.gatherings:
                self.intention = 'PATHFINDING_HOME'
            elif self.findClosestHarvestable(tileData, actors):
                self.intention = 'PATHFINDING_HARVESTABLE'
            else:
                self.intention = 'RESTING'
    
    def doResting(self):
        if self.staminaFull:
            p = random.random()
            if p < 0.5:
                self.intention = 'PATHFINDING_HARVESTABLE'
            else:
                self.intention = 'ROAMING'
        else:
            pass
    

    def doStockUpAllHarvestables(self, ws):
        
        STOCK_WAIT_COST = 20
        
        if not self.gatherings or not self.isMyHomeNeighbor(ws):
            self.intention = 'PATHFINDING_HARVESTABLE'
            return
        
        if self.gatherings and self.isMyHomeNeighbor(ws):
            
            self.angle = self.getAngleTo(ws.actorsDict[self.home()].location)
            
            if self.waitGauge is None:
                self.waitGauge = STOCK_WAIT_COST
                
            self.waitGauge -= 0.25
                    
            if self.waitFinished:
                k = self.gatherings.iterkeys().next()
                assert self.gatherings[k] > 0
                self.gatherings[k] -= 1
                self.home().send((self.channel, "ACQUIRE", k, 1))
                if self.gatherings[k] <= 0:
                    del self.gatherings[k]
                
                self.waitGauge = None
                

    def drawFadeoutText(self, text):
        self.sendDisplay((self.channel, 'DRAW_FADEOUT_TEXT', text, self.location))
        
    def handleWorldState(self, ws, myProp):
        
        self.deltaTime = ws.time - self.time
        self.time = ws.time
        
        self.location = myProp.location
        
        actors = ws.actors
        tileData = ws.tileData
        
        if self.intention is 'ROAMING':
            
            if self.roamingTarget is None or self.isNear(self.roamingTarget):
                self.roamingTarget = self.getRandomLocationAround(self.roamingRadius)
            
            self.angle = self.getAngleTo(self.roamingTarget)
            
            self.velocity = 2
            
            if self.stamina < 0:
                self.intention = 'RESTING'
                self.roamingTarget = None
                
            pass
        
        elif self.intention is 'RESTING':
            
            self.doResting()
            
        elif self.intention is 'PATHFINDING_HOME':
            
            homeProp = ws.actorsDict.get(self.home(), None) if self.home else None
            if homeProp:
                self.doPathFindingPixelCoord(tileData,
                                             'STOCK_UP_ALL_HARVESTABLES',
                                             *homeProp.location)
            else:
                self.intention = 'RESTING'
            
        elif self.intention is 'PATHFINDING_HARVESTABLE':
            
            h, hProp = self.findClosestHarvestable(tileData, actors)
            
            if h:
                self.doPathFindingPixelCoord(tileData, 'HARVESTING',
                                             *hProp.location)
            else:
                self.intention = 'RESTING'
        
        elif self.intention is 'HARVESTING':
            
            self.doHarvesting(tileData, actors)
            
        elif self.intention is 'STOCK_UP_ALL_HARVESTABLES':
            
            self.doStockUpAllHarvestables(ws)
            
            
        else:
            raise RuntimeError('%s: Unknown intention %s received.'
                               % (self, self.intention))
            
        
        #self.angle += 10.0 * (1.0 / msgArgs[0].updateRate)
        if self.angle >= 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
            
        updateMsg = (self.channel, "UPDATE_VECTOR",
                     self.angle, self.velocity)
        
        #print self.angle
        self.world.send(updateMsg)
        
        # 마지막에 깎자
        self.stamina -= self.deltaTime
        #self.world.send((self.channel, "UPDATE_MY_STAMINA", self.stamina))
        
        # If stamina remains below the negative value,
        # the hitpoints will be decreased.
        if self.staminaDepleted:
            if self._starvationWaitGauge is None:
                self._starvationWaitGauge = 2000
            else:
                self._starvationWaitGauge -= 1
                
            if self._starvationWaitGauge <= 0:
                self.hitpoints -= 1
                self._starvationWaitGauge = None
                if self.dead:
                    self.deathReason = 'STARVATION'
        else:
            self._starvationWaitGauge = None
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            self.handleWorldState(*msgArgs)
            
        elif msg == "COLLISION":
            pass

        elif msg == "ACQUIRE":
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            self.gatherings[gathering] = self.gatherings.get(gathering, 0) + gatheringCount
            self.drawFadeoutText('%s+%d' % (gathering, gatheringCount))
            
        elif msg == "IDENTIFY_HARVEST_RESULT":
            #print self.channel, self.instanceName, "HARVESTED:", self.gatherings
            print self,self.intention
            msgArgs[0].append(self.gatherings)
        
        elif msg == "ADD_STAMINA":
            old = self.stamina
            self.stamina += msgArgs[0]
            if old != self.stamina:
                self.drawFadeoutText('%s+%d' % ('STAMINA', msgArgs[0]))
            
        elif msg == "CAN_STOCK_GATHERINGS":
            while self.gatherings:
                k,v = self.gatherings.popitem()
                sentFrom.send((self.channel, "ACQUIRE", k, v))
                
        elif msg == 'ATTACK':
            self.hitpoints -= msgArgs[0]
            
        elif msg == 'YOU_ARE_DEAD':
            self.info('I am dead by %s.' % self.deathReason)
        elif msg == 'NEIGHBORS_LEFT':
            self._neighbors.difference_update(msgArgs[0])
        elif msg == 'NEIGHBORS_ENTERED':
            self._neighbors.update(msgArgs[0])
        else:
            raise RuntimeError('%s: Unknown message received - %s' % (self, msg))
