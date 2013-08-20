# coding=utf-8
import stackless  # @UnresolvedImport
import random
import logging
from actor import SActor, ActorProperties

class SPrey(SActor):
    def __init__(self, world, location=(0,0), angle=0, velocity=0,
                 hitpoints=10, homeLocation=None, instanceName="",
                 stamina=100, maxStamina=100, attackPower=1,
                 intention='RESTING'):
        
        SActor.__init__(self, instanceName)
        self.time = 0
        self.deltaTime = 0
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.stamina = stamina
        self.maxStamina = maxStamina
        self.restingHome = None
        self.roamingPath = None
        self.restFor = 5
        self.world.send((self.channel, "JOIN",
                         ActorProperties('001-Fighter01',
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         animatedSprite=True,
                                         instanceName=self.instanceName)))

        self.changeIntention(intention)
        
        logging.info('A prey [%s] created.' % self.instanceName)
        
    def changeIntention(self, intention):
        
        if intention == 'ROAMING':
            self.velocity = 10
        elif intention == 'RESTING':
            self.velocity = 0
            self.restFor = 6 + random.random() * 6
        else:
            raise RuntimeError('Unknown intention for %s' % self)

        self.lastIntentionTime = self.time        
        self.intention = intention
        
        self.world.send((self.channel, 'UPDATE_INTENTION', intention))

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
            
            path = tileData.findPath(int(self.location[0]//32),
                                     int(self.location[1]//32),
                                     int(goalTile[0]//32),
                                     int(goalTile[1]//32))

        return path
    
    def getLocationFromTile(self, tileIndex):
        return (tileIndex[0]*32+16, tileIndex[1]*32+16)
        
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            self.deltaTime = msgArgs[0].time - self.time
            self.time = msgArgs[0].time
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            if self.intention == 'ROAMING':
                
                # If I don't have a roaming path, create a new one.
                if not self.roamingPath:
                    tileData = msgArgs[0].tileData
                    self.roamingPath = self.findNewRoamingPathWithin(4,
                                                                     tileData)
                    
                # Or check if I am near the current roaming target
                # location.
                elif self.isNear(self.getLocationFromTile(self.roamingPath[0]),
                                 9):
                     
                    # If near, remove the current target location
                    self.roamingPath.pop(0)
                    
                # Update my angle and velocity if the roaming path available.
                if self.roamingPath:
                    
                    angle = self.getLocationFromTile(self.roamingPath[0])
                    self.angle = self.getAngleTo(angle)
                                    
                # Or change to the RESTING state.
                else:
                    self.changeIntention('RESTING')
                    
                    
                
            elif self.intention == 'RESTING':
                
                #self.world.send((self.channel, 'NO_MORE_TICK_EVENT'))
                
                self.restFor -= self.deltaTime
                
                # Return to the roaming state if resting is over.
                if self.restFor <= 0:
                    self.changeIntention('ROAMING')
                                
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle, self.velocity)
            self.world.send(updateMsg)
            
            self.stamina -= self.deltaTime
            
            
        elif msg == "COLLISION":
            pass
