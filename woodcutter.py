# coding=utf-8
import stackless  # @UnresolvedImport
import random, math
from collections import OrderedDict
from actor import SActor, ActorProperties

class SWoodcutter(SActor):
    def __init__(self, world, location=(0,0), angle=135, velocity=0, hitpoints=10, homeLocation=None, instanceName="", stamina=5, maxStamina=7):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.time = 0
        self.deltaTime = 0
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.homeLocation = homeLocation
        self.world = world
        self.havestingTask = None
        self.havestTarget = None
        self.havestTargetProp = None
        self.gatherings = OrderedDict()
        self.havestingChannel = stackless.channel()
        self.lastHavestTime = -1
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
                nextIntention = 'WOODCUTTING'
            else:
                nextIntention = 'RESTING'
            
            if self.intention != nextIntention:
                self.intention = nextIntention
                return True
            
        return False
    
    def getRandomLocationAround(self, r):
        
        return (self.location[0] + (2*random.random() - 1) * r,
                self.location[1] + (2*random.random() - 1) * r)
    
    def isNear(self, loc):
        
        return self.sqDistanceWithMe(loc) < 25
    
    def sqDistanceWithMe(self, loc):
        
        return sum(((self.location[i] - loc[i])**2 for i in [0,1]))
    
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
            
            #print self.intention
            
            if self.intention is 'WOODCUTTING':
            
                havestables = [h for h in msgArgs[0].actors if h[1].havestable]
                
                #print havestables
                
                # 채집물이 월드에 존재하고, 현재 채집물 타겟이 없고, 스태미너가 어느정도 있다면
                # 현재 가장 가까운 채집물을 새 채집물 타겟으로 설정한다.
                if havestables and self.havestTarget is None and self.stamina >= self.maxStamina/2:
                    
                    h = min(havestables, key=lambda h: self.sqDistanceWithMe(h[1].location))
                    
                    self.havestTarget = h[0]
                    self.havestTargetProp = h[1]
                

                if self.stamina <= 0:
                    self.havestTarget = None
                    self.havestTargetProp = None
                    self.intention = 'RESTING'
                
                if self.havestTargetProp:
                    self.angle = math.degrees(math.atan2(-(self.location[0] - self.havestTargetProp.location[0]),
                                                         self.location[1] - self.havestTargetProp.location[1]))
                    self.velocity = 50
                    
                else:
                    self.intention = 'RESTING'
                
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
            # Send a HAVEST message from the woodcutter to the tree. (NOT FROM THE TREE TO THE WOODCUTTER)
            if self.havestingTask is None:
                
                if self.channel is msgArgs[0]:
                    target = msgArgs[1]
                    targetProp = msgArgs[1+2]
                elif self.channel is msgArgs[1]:
                    raise RuntimeError("Collision argument error")
                    #target = msgArgs[0]
                    #targetProp = msgArgs[0+2]
                else:
                    raise RuntimeError("What happened?")
                
                if target is not self.havestTarget:
                    return
                
                #print "Woodcutter channel =",self.channel, "/targetProp.name=", targetProp.name
                
                if targetProp.havestable:
                
                    #print "Woodcutter channel =",self.channel
                    if self.lastHavestTime < 0 or self.time - self.lastHavestTime > 5:
                        #print self.channel, "--HAVEST-->", target, target.balance, target.closed, target.closing
                        target.send((self.channel, "HAVEST"))
                        self.lastHavestTime = self.time
                    
                    
                    #self.havestingTask = stackless.tasklet(self.havestWood)(target)
                    
                #print "COLLISION!!!"
                #self.havestingChannel.send((sentFrom, msg, msgArgs))
                
                
            
        elif msg == "ACQUIRE":
            gathering = msgArgs[0]
            gatheringCount = msgArgs[1]
            if self.gatherings.has_key(gathering):
                self.gatherings[gathering] += gatheringCount
            else:
                self.gatherings[gathering] = gatheringCount

        elif msg == "IDENTIFY_HAVEST_RESULT":
            #print self.channel, self.instanceName, "HAVESTED:", self.gatherings
            msgArgs[0].append(self.gatherings)
        
        elif msg == "ADD_STAMINA":
            self.stamina += msgArgs[0]
            
        elif msg == "CAN_STOCK_GATHERINGS":
            while self.gatherings:
                k,v = self.gatherings.popitem()
                sentFrom.send((self.channel, "ACQUIRE", k, v))
            
