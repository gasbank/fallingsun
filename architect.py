# coding=utf-8
import random, math
from collections import OrderedDict
from actor import SActor, ActorProperties
from home import SHome

class SArchitect(SActor):
    def __init__(self, world, location=(0,0), angle=0, velocity=0, hitpoints=10, homeLocation=None, instanceName="", stamina=5, maxStamina=7):
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
        self.intention = 'ROAMING'
        self.lastIntentionTime = -1
        self.roamingTarget = None
        self.lastRoamingTargetTime = None
        self.restingHome = None
        self.gatherings = OrderedDict()
        self.homeNumber = 0
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         instanceName=self.instanceName)))
    
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
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            self.checkIntention()
            
            #print self.intention
            
            if self.intention is 'BUILDING':
                
                if self.isNear(self.targetBuildingLoc):
                    
                    if self.gatherings.get('WOOD', 0) == 10:
                        
                        self.gatherings.clear()
                    
                        #self.world.send((self.channel, "SPAWN_HOME", self.location))
                        
                        self.homeNumber += 1
                        SHome(self.world,
                              location=self.location,
                              instanceName=("Architect Home #%d" % self.homeNumber),
                              staminaRefillSpeed=1)
                    
                    self.intention = 'ROAMING'
                
                else:
                    
                    self.angle = self.getAngleTo(self.targetBuildingLoc)
                    self.velocity = 15
                    
                pass
                                
            elif self.intention is 'ROAMING':
                
                if self.roamingTarget is None or self.isNear(self.roamingTarget):
                    self.roamingTarget = self.getRandomLocationAround(50)
                
                self.angle = self.getAngleTo(self.roamingTarget)
                
                self.velocity = 2
                
                if self.stamina < 0:
                    self.roamingTarget = None
                    self.intention = 'RESTING'
                    
                pass
            
            elif self.intention is 'RESTING':
                
                if self.homeLocation:
                    self.angle = self.getAngleTo(self.homeLocation)
                    
                else:
                    self.velocity = 0

                # 스태미너가 꽉 찼으면 다음 액션을 취하자!
                if self.stamina >= self.maxStamina:
                    self.intention = 'ROAMING'
                    
                    # 집에서 쉬고 있었다면 일정 확률로 나무를 요구하자
                    p = random.random()
                    if p < 0.9 and self.restingHome:
                        
                        self.restingHome.send((self.channel, 'GIVE_ME_GATHERINGS', {'WOOD':10})) 
                                
            
            #self.angle += 10.0 * (1.0 / msgArgs[0].updateRate)
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle, self.velocity)
            self.world.send(updateMsg)
            
            # 마지막에 깎자
            self.stamina -= self.deltaTime
            
            
        elif msg == "COLLISION":
            
            target = msgArgs[1]
            targetProp = msgArgs[1+2]
                
            if targetProp.name == 'SHome' and self.intention == 'RESTING':
                self.restingHome = target
                #print 'Architect meets Home'
                        
        elif msg == "ADD_STAMINA":
            self.stamina += msgArgs[0]
            if self.stamina > self.maxStamina:
                self.stamina = self.maxStamina
            
        elif msg == "ACQUIRE":
            
            reply = msgArgs[0]
            
            if reply.get('WOOD', 0) == 10:
                
                self.gatherings.clear()
                self.gatherings.update(reply)
                
                self.intention = 'BUILDING'
                self.targetBuilding = 'HOME'
                self.targetBuildingLoc = self.getRandomLocationAround2(100, 300)
