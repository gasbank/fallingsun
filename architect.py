# coding=utf-8
import random, math
from actor import SActor, ActorProperties

class SArchitect(SActor):
    def __init__(self, world, location=(0,0), angle=0, velocity=0, hitpoints=10, homeLocation=None, instanceName="", stamina=100, maxStamina=140):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.time = 0
        self.deltaTime = 0
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.stamina = stamina
        self.maxStamina = maxStamina
        self.intention = ''
        self.lastIntentionTime = -1
        self.roamingTarget = None
        self.lastRoamingTargetTime = None 
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
        
    def checkIntention(self):
        if not self.intention:
            p = random.random()
            if p < 0.2:
                nextIntention = 'ROAMING'
            elif p < 0.4:
                nextIntention = 'BUILDING'
            else:
                nextIntention = 'RESTING'
            
            if self.intention != nextIntention:
                self.intention = nextIntention
                return True
            
        return False
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]

        if msg == "WORLD_STATE":
            self.deltaTime = msgArgs[0].time - self.time
            self.time = msgArgs[0].time
            
            self.stamina -= self.deltaTime
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            self.checkIntention()
            
            if self.intention is 'BUILDING':
                
                if self.isNear(self.targetBuildingLoc):
                    
                    pass
                
                else:
                    
                    self.angle = self.getAngleTo(self.targetBuildingLoc)
                    self.velocity = 5
                    
                pass
                                
            elif self.intention is 'ROAMING':
                
                if self.roamingTarget is None or self.isNear(self.roamingTarget):
                    self.roamingTarget = self.getRandomLocationAround(100)
                
                self.angle = math.degrees(math.atan2(-(self.location[0] - self.roamingTarget[0]),
                                                     self.location[1] - self.roamingTarget[1]))
                
                self.velocity = 2
                
                if self.stamina < 0:
                    self.roamingTarget = None
                    self.intention = 'RESTING'
                    
                pass
            
            elif self.intention is 'RESTING':
                
                if self.homeLocation:
                    self.angle = math.degrees(math.atan2(-(self.location[0] - self.homeLocation[0]),
                                                         self.location[1] - self.homeLocation[1]))
                    
                else:
                    self.velocity = 0
                    
                if self.stamina >= self.maxStamina:
                    p = random.random()
                    if p < 0.5:
                        self.intention = 'WOODCUTTING'
                    else:
                        self.intention = 'ROAMING'
            
            
            #self.angle += 10.0 * (1.0 / msgArgs[0].updateRate)
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle, self.velocity)
            self.world.send(updateMsg)
            
        elif msg == "COLLISION":
            pass                
                        
        elif msg == "ADD_STAMINA":
            self.stamina += msgArgs[0]
            
        elif msg == "CAN_BUILD":
            
            if msgArgs[0] == 'HOME' and self.intention != 'BUILDING':
                
                sentFrom.send((self.channel, 'GIVE_ME_GATHERINGS', {'WOOD':20}))
        
        elif msg == "ACQUIRE":
            
            if msgArgs[0] == 'HOME' and msgArgs[1] == 20:
                
                self.intention = 'BUILDING'
                self.targetBuilding = 'HOME'
                self.targetBuildingLoc = self.getRandomLocationAround2(100, 300)
