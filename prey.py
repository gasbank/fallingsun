# coding=utf-8
import stackless  # @UnresolvedImport
import random
import logging
from actor import SActor, ActorProperties

class SPrey(SActor):
    
    @property
    def angle(self): return self._angle
    @angle.setter
    def angle(self, value):
        if self._angle != value:
            self._angle = value
            self._angleDirty = True
            
    @property
    def velocity(self): return self._velocity
    @velocity.setter
    def velocity(self, value):
        if self._velocity != value:
            self._velocity = value
            self._velocityDirty = True
    
    def __init__(self, world, location=(0,0), angle=0, velocity=0,
                 hitpoints=10, homeLocation=None, instanceName="",
                 stamina=100, maxStamina=100, attackPower=1,
                 intention='RESTING', roamingVelocity=30):
        
        SActor.__init__(self, instanceName)
        self._angle = self._angleDirty = None
        self._velocity = self._velocityDirty = None
        self.intention = None
        self.roamingVelocity = roamingVelocity
        
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
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         animatedSprite=True,
                                         instanceName=self.instanceName)))

        self.changeIntention(intention)
        
        self.debug('Created.')
        
    def changeIntention(self, intention):
        
        if intention == 'ROAMING':
            self.velocity = self.roamingVelocity
        elif intention == 'RESTING':
            self.velocity = 0
            self.restFor = 6 + random.random() * 6
        elif intention == 'SYNCING':
            self.velocity = 0
        else:
            raise RuntimeError('Unknown intention for %s' % self)

        self.lastIntentionTime = self.time        
        self.intention = intention
        
        self.world.send((self.channel, 'UPDATE_INTENTION', intention))
        

    def sendUpdateVector(self):
        if self._angleDirty or self._velocityDirty:
            
            self.world.send((self.channel, "UPDATE_VECTOR", self.angle,
                             self.velocity))
            
            self._angleDirty = self._velocityDirty = False
    

    def handleWorldState(self, ws, myProp):
        
        self.deltaTime = ws.time - self.time
        self.time = ws.time
        
        self.location = myProp.location
        
        if self.intention == 'ROAMING':
            
            # If I don't have a roaming path, create a new one.
            if not self.roamingPath:
                tileData = ws.tileData
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
            
        elif self.intention == 'SYNCING':
            pass
        elif self.intention is None:
            pass
        else:
            raise RuntimeError('Unknown intention: %s' % self.intention)
                            
        if self.angle >= 360:
            self.angle -= 360
        
        self.sendUpdateVector()
        
        self.stamina -= self.deltaTime
    
    
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            self.handleWorldState(*msgArgs)
            
        elif msg == "COLLISION":
            pass
