# coding=utf-8
import random
from collections import OrderedDict
from actor import SActor, ActorProperties
from level import TileNeighborhood4

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
    def staminaFull(self):
        return self.stamina >= self.maxStamina
    
    def __init__(self, world, location=(0,0), angle=135, velocity=0,
                 hitpoints=10, homeLocation=None, instanceName="",
                 stamina=5, maxStamina=7, roamingRadius=100,
                 intention='RESTING', home=None):
        
        SActor.__init__(self, instanceName)
        self.time = 0
        self.deltaTime = 0
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.harvestTarget = None
        self.harvestTargetProp = None
        self.gatherings = OrderedDict()
        self.lastHarvestTime = -1
        self.stamina = stamina
        self.maxStamina = maxStamina
        self.roamingTarget = None
        self.lastRoamingTargetTime = None
        self.roamingRadius = roamingRadius
        self.roamingPath = None
        self._lastIntentionTime = -1
        self._intention = None
        self._waitGauge = None
        self.home = home
        
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
    
    def isMyHomeNeighbor(self, tileData, actors):
        
        return self.isNeighborTiles(tileData, self.getHomeProp(actors).location)
    
    def getHomeProp(self, actors):
        
        homeList = [h for h in actors if h[0] is self.home]
        assert len(homeList) == 1
        return homeList[0][1]
    
    def findClosestHarvestable(self, tileData, actors):
        harvestables = [h for h in actors if h[1].harvestable
                       and h[1].hitpoints > 0]
    
        if harvestables:
            return min(harvestables, key=lambda h: self.manDistanceWithMe(h[1].location))
        
        return None
    

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
            self.waitGauge -= 0.25
            
            if self.waitFinished:
            
                self.info('--%s--> %s' % ('HARVEST',
                                          self.harvestTargetProp.instanceName))
                self.harvestTarget.send((self.channel, "HARVEST"))
                
                # Refill the wait gauge.
                self.waitGauge = HARVEST_WAIT_COST
        
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
    

    def doStockUpAllHarvestables(self, tileData, actors):
        
        STOCK_WAIT_COST = 20
        
        if not self.gatherings or not self.isMyHomeNeighbor(tileData, actors):
            self.intention = 'PATHFINDING_HARVESTABLE'
            return
        
        if self.gatherings and self.isMyHomeNeighbor(tileData, actors):
            
            self.angle = self.getAngleTo(self.getHomeProp(actors).location)
            
            if self.waitGauge is None:
                self.waitGauge = STOCK_WAIT_COST
                
            self.waitGauge -= 0.25
                    
            if self.waitFinished:
                k = self.gatherings.iterkeys().next()
                assert self.gatherings[k] > 0
                self.gatherings[k] -= 1
                self.home.send((self.channel, "ACQUIRE", k, 1))
                if self.gatherings[k] <= 0:
                    del self.gatherings[k]
                
                self.waitGauge = None
                
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            
            self.deltaTime = msgArgs[0].time - self.time
            self.time = msgArgs[0].time
           
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            tileData = msgArgs[0].tileData
            #print self.intention
            
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
                                              
                self.doPathFinding(tileData,
                                   int(self.homeLocation[0]//32),
                                   int(self.homeLocation[1]//32),
                                   'STOCK_UP_ALL_HARVESTABLES')
                
            elif self.intention is 'PATHFINDING_HARVESTABLE':
                
                h = self.findClosestHarvestable(msgArgs[0].tileData,
                                                msgArgs[0].actors)
                
                if h:
                    self.doPathFinding(tileData,
                                       int(h[1].location[0]//32),
                                       int(h[1].location[1]//32),
                                       'HARVESTING')
                else:
                    self.intention = 'RESTING'
            
            elif self.intention is 'HARVESTING':
                
                self.doHarvesting(msgArgs[0].tileData, msgArgs[0].actors)
                
            elif self.intention is 'STOCK_UP_ALL_HARVESTABLES':
                
                self.doStockUpAllHarvestables(msgArgs[0].tileData,
                                              msgArgs[0].actors)
                
                
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
            
            # 마지막에 깎지 
            self.stamina -= self.deltaTime
            #self.world.send((self.channel, "UPDATE_MY_STAMINA", self.stamina))
            
            # If stamina remains below the certain negative value,
            # the hitpoints will be decreased.
            if self.stamina < -100:
                self.setHitpoints(self.hitpoints - 1)
                if self.hitpoints <= 0:
                    self.deathReason = 'STARVATION'
            
            
        elif msg == "COLLISION":
            
            if self.channel is msgArgs[0]:
                target = msgArgs[1]
                targetProp = msgArgs[1+2]
            elif self.channel is msgArgs[1]:
                raise RuntimeError("Collision argument error")
                #target = msgArgs[0]
                #targetProp = msgArgs[0+2]
            else:
                raise RuntimeError("What happened?")
            
            self.debug('Collision with %s' % targetProp.name)

        elif msg == "ACQUIRE":
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            self.gatherings[gathering] = self.gatherings.get(gathering, 0) + gatheringCount

        elif msg == "IDENTIFY_HARVEST_RESULT":
            #print self.channel, self.instanceName, "HARVESTED:", self.gatherings
            print self,self.intention
            msgArgs[0].append(self.gatherings)
        
        elif msg == "ADD_STAMINA":
            self.stamina += msgArgs[0]
            if self.stamina > self.maxStamina:
                self.stamina = self.maxStamina
            
        elif msg == "CAN_STOCK_GATHERINGS":
            while self.gatherings:
                k,v = self.gatherings.popitem()
                sentFrom.send((self.channel, "ACQUIRE", k, v))
                
        elif msg == 'ATTACK':
            self.setHitpoints(self.hitpoints - msgArgs[0])
            
        elif msg == 'YOU_ARE_DEAD':
            self.info('I am dead by %s.' % self.deathReason)
        else:
            raise RuntimeError('%s: Unknown message received - %s' % (self, msg))

    def setHitpoints(self, newValue):
        self.hitpoints = newValue
        self.world.send((self.channel, "UPDATE_MY_HP", self.hitpoints))
        