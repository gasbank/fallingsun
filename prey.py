# coding=utf-8
import stackless  # @UnresolvedImport
import random
import logging
from actor import SActor, ActorProperties, UnknownMessageError
import weakref
import dialog

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
                 intention='RESTING', roamingVelocity=30, conversation=None):
        
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
        self.clearVocaTarget()
        self.conversation = conversation
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         location=location,
                                         angle=self.angle,
                                         velocity=self.velocity,
                                         height=32,
                                         width=16,
                                         hitpoints=self.hitpoints,
                                         animatedSprite=True,
                                         instanceName=self.instanceName,
                                         conversation=self.conversation)))

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
    
    
    def handleAvailableVocas(self, sentFrom, vocas, conversation):
        
        if self._dialogContext is None:
            self._dialogContext = dialog.Context(conversation, self.channel,
                                                 sentFrom, self.world)

        if self._display:
            self._display.send((self.channel, 'SET_DIALOG_CONTEXT',
                                self._dialogContext))
        '''
        self._vocaTarget = weakref.ref(sentFrom)
        self._vocas = list(vocas)
        
        if self._display:
            self._display.send((self.channel, 'SET_VOCAS', str(sentFrom.name),
                                sentFrom, vocas, dialog))'''

    def clearVocaTarget(self):
        self._vocaTarget = None
        self._vocas = None
        self._dialogContext = None
        
        if self._display:
            self._display.send((self.channel, 'CLEAR_VOCAS'))

    def handleVocaChosen(self, chosen):
        if self._dialogContext and self._dialogContext.isChoice:
            if self._dialogContext.choose(chosen):
            
                if self._display:
                    self._display.send((self.channel, 'SET_DIALOG_CONTEXT',
                                        self._dialogContext))            
            #self._vocaTarget().send((self.channel, 'REQUEST_VOCA', v))
    
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        
        if msg == "WORLD_STATE":
            self.handleWorldState(*msgArgs)
            
        elif msg == "COLLISION":
            pass
        elif msg == 'I_AM_DISPLAY':
            self._display = sentFrom
        elif msg == 'MOVE_PAWN':
            
            direction, pressed = msgArgs
            if pressed: return
            
            if direction == 'N':
                dLoc = (0,-32)
            elif direction == 'E':
                dLoc = (32,0)
            elif direction == 'S':
                dLoc = (0,32)
            elif direction == 'W':
                dLoc = (-32,0)
            else:
                raise RuntimeError('Unknown direction %s', direction)

            self.world.send((self.channel, 'REQUEST_RELATIVE_TELEPORT', dLoc))
            pass
        elif msg == 'F_PRESSED':
            if msgArgs[0]:
                self.world.send((self.channel, 'QUERY_NEIGHBORS_VOCA', 1))
        elif msg == 'VOCA_CHOSEN':
            self.handleVocaChosen(msgArgs[0])
        elif msg == 'TELEPORTED':
            self.clearVocaTarget()
        elif msg == 'QUERY_RESULT':
            pass
        elif msg == 'AVAILABLE_VOCAS':
            self.handleAvailableVocas(sentFrom, *msgArgs)
        else:
            raise UnknownMessageError(msg, sentFrom)
