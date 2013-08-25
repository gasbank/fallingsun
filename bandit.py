# coding=utf-8
import random, logging
from actor import SActor, ActorProperties

class SBandit(SActor):
    def __init__(self, world, location=(0,0), angle=0, velocity=0, hitpoints=10, homeLocation=None, instanceName="", stamina=100, maxStamina=100, attackPower=1):
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
        self.intention = 'ATTACKING'
        self.lastIntentionTime = -1
        self.roamingTarget = None
        self.lastRoamingTargetTime = None
        self.restingHome = None
        self.attackPower = attackPower
        self.attackTarget = None
        self.attackTargetProp = None
        self.lastAttackTime = None
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         instanceName=self.instanceName)))
        
        logging.info('A bandit [%s] created.' % self.instanceName)
        
    def checkIntention(self):
        if not self.intention:
            p = random.random()
            if p < 0.2:
                nextIntention = 'ROAMING'
            elif p < 0.4:
                nextIntention = 'ATTACKING'
            else:
                nextIntention = 'RESTING'
            
            if self.intention != nextIntention:
                self.intention = nextIntention
                return True
            
        return False
    
    def findNewAttackTarget(self, actors):

        targets = [a for a in actors if a[1].name in ['SWoodcutter', 'SArchitect']]
        
        if targets:
            a = min(targets, key=lambda a: self.sqDistanceWithMe(a[1].location))
        else:
            a = (None, None)
        
        return a[0], a[1]
    
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]

        if msg == "WORLD_STATE":
            self.deltaTime = msgArgs[0].time - self.time
            self.time = msgArgs[0].time
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            self.checkIntention()
            
            #print self.intention
            
            if self.intention is 'ATTACKING':
                
                if self.attackTargetProp is None:
                    
                    self.attackTarget, self.attackTargetProp = self.findNewAttackTarget(msgArgs[0].actors)
                    
                    #print 'TARGET',self.attackTarget, self.attackTargetProp
                    
                if self.attackTargetProp and self.attackTargetProp.hitpoints > 0:
                    self.angle = self.getAngleTo(self.attackTargetProp.location)
                    self.velocity = 5
                else:
                    self.attackTargetProp = None
                    self.roamingTarget = None
                    self.intention = 'RESTING'
                    
                if self.stamina < 0:
                    self.attackTargetProp = None
                    self.roamingTarget = None
                    self.intention = 'RESTING'
                                
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

                if self.stamina >= self.maxStamina:
                    self.intention = 'ROAMING'
                    #print 'FULL STAMINA'
                    p = random.random()
                    if p < 0.9:
                        #print 'A!!!!!!!!'
                        self.intention = 'ATTACKING' 
            
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle, self.velocity)
            self.world.send(updateMsg)
            
            self.stamina -= self.deltaTime
            
            
        elif msg == "COLLISION":
            
            target = msgArgs[1]
            targetProp = msgArgs[1+2]
                
            if self.intention == 'ATTACKING' and targetProp == self.attackTargetProp:
                #self.channel.send((self.channel, 'MEET_TARGET', target, targetProp))
                
                if not self.lastAttackTime or self.time - self.lastAttackTime > 5:
                    target.send((self.channel, 'ATTACK', self.attackPower))
                    self.lastAttackTime = self.time
                        
        elif msg == "ADD_STAMINA":
            self.stamina += msgArgs[0]
            if self.stamina > self.maxStamina:
                self.stamina = self.maxStamina
        
        elif msg == "IDENTIFY_HARVEST_RESULT":
            print self,self.intention,self.stamina
