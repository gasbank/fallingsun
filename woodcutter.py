import stackless
import random, math
from collections import OrderedDict
from actor import SActor, ActorProperties

class SWoodcutter(SActor):
    def __init__(self, world, location=(0,0), angle=135, velocity=0, hitpoints=10, homeLocation=None, instanceName=""):
        self.instanceName = instanceName
        SActor.__init__(self)
        self.time = 0
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
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
        
            self.time = msgArgs[0].time
            
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel: break
                    
            self.location = actor[1].location
            
            
            havestables = []
            for actor in msgArgs[0].actors:
                actorProp = actor[1]
                if actorProp.havestable:
                    havestables.append(actor)
            
            if havestables and self.havestTarget is None:
                havestable = random.choice(havestables)
                self.havestTarget = havestable[0]
                self.havestTargetProp = havestable[1]
                
            if self.havestTargetProp and not self.havestTargetProp.havestable:
                self.havestTarget = None
                self.havestTargetProp = None
            #print self.havestTarget, self.havestTargetProp
            """
            for actor in msgArgs[0].actors:
                if actor[1].name == "STree":
                    self.havestTarget = actor[0]
                    havestTargetProp = actor[1]
            """     
            
            if self.havestTargetProp:
                self.angle = math.degrees(math.atan2(-(self.location[0] - self.havestTargetProp.location[0]),
                                                     self.location[1] - self.havestTargetProp.location[1]))
                #self.velocity = 3
            elif self.homeLocation:
                self.angle = math.degrees(math.atan2(-(self.location[0] - self.homeLocation[0]),
                                                     self.location[1] - self.homeLocation[1]))
                #self.velocity = 6
                
            else:
                #self.velocity = 0
                pass
            
            
            
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
                    target = msgArgs[0]
                    targetProp = msgArgs[0+2]
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
        
