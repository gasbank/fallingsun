from actor import ActorProperties, NamedTasklet, UnknownMessageError, UnauthorizedAccessError
from netactor import SNetActor
from prey import SPrey
from sight import SSight
import connection
import socket
import struct

class SUser(SNetActor):
    
    def __init__(self, world, instanceName, connection):
        SNetActor.__init__(self, instanceName)
        self.world = world
        self.connection = connection
        self.sight = None
        self.pawn = None
        
        sightX, sightY = 4, 4
        self.sight = SSight(world, location=(32 * sightX, 32* sightY),
                            instanceName=instanceName+'Sight',
                            sightRange=2, user=self.channel).channel
        
        self.pawn = SPrey(world, location=(32*sightX+16,32*sightY+16),
                          velocity=0, angle=90,
                          instanceName=self.instanceName+'Pawn', stamina=100,
                          maxStamina=100, intention='SYNCING').channel
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))
        
        self.info('about to send OWNERSHIP...!')
        self.sendCommand(('OWNERSHIP', id(self.pawn)))
        self.info('OWNERSHIP sent...!')
        # The tasklet will hold a reference to the user keeping the instance
        # alive as long as it is handling commands.
        NamedTasklet(self.Run)()
        
    def getConnection(self):
        return self.connection

    def Run(self):
        try:
            while self.HandleCommand():
                pass

            self.OnUserDisconnection()
        except connection.RemoteDisconnectionError:
            self.OnRemoteDisconnection()
            self.connection = None
        finally:
            if self.connection:
                self.connection.disconnect()
                self.connection = None
            
    def HandleCommand(self):
        try:
            cmd, cmdArgs = self.recvCommand()
        except ValueError:
            self.info('invalid value received.')
            return False
        except socket.error:
            raise connection.RemoteDisconnectionError
        except EOFError:
            return False
        except struct.error:
            return False
        
        try:
            self.processMessageMethod((self.connection, cmd, cmdArgs))
        except UnauthorizedAccessError, e:
            self.warn(e)
        
        return True

    def OnRemoteDisconnection(self):
        self.world.send_sequence([(self.sight, 'KILLME'),
                                  (self.pawn, 'KILLME'),
                                  (self.channel, 'KILLME')])
        self.info("Disconnected %d (remote)" % id(self))

    def OnUserDisconnection(self):
        self.world.send_sequence([(self.sight, 'KILLME'),
                                  (self.pawn, 'KILLME'),
                                  (self.channel, 'KILLME')])
        self.info("Disconnected %d (local)" % id(self))
        
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'SEND_SPAWN':
            if not self.connection:
                return
            
            actors = []
            for na, np in msgArgs[0]:
                if na() is None or np() is None:
                    continue
                '''
                if np().name not in ['SPrey']:
                    continue
                '''
                name = 'SHeadman' if na() is self.pawn else np().name
                #name = np.name  
                p = (id(na()), name,
                     tuple([int(v) for v in np().location]),
                     int(np().angle), int(np().velocity))
                actors.append(p)
                
            for a in actors:
                self.sendCommand(('SPAWN', [a]))

        elif msg == 'SEND_DESPAWN':
            if not self.connection:
                return
            
            actors = []
            for na, np in msgArgs[0]:
                '''
                if na() is None or np() is None:
                    continue
                if np().name not in ['SPrey']:
                    continue
                '''
                
                actors.append((id(na()),))
            
            for a in actors:    
                self.sendCommand(('DESPAWN', [a]))

        elif msg == 'SEND_UPDATE_VECTOR':
            if not self.connection:
                return
            
            self.sendCommand(('UPDATE_VECTOR', (id(msgArgs[0]),
                                               tuple([int(v) for v in msgArgs[1].location]),
                                               int(msgArgs[1].angle),
                                               int(msgArgs[1].velocity))))

        elif msg == 'UPDATE_VECTOR':
            actorId, (angle, velocity) = msgArgs[0]
            
            if sentFrom is self.connection:
                if id(self.pawn) != actorId:
                    raise UnauthorizedAccessError(msg, sentFrom)
            
                self.world.send((self.pawn, 'UPDATE_VECTOR', angle, velocity))
                
        elif msg == 'CLOSE_SOCKET':
            if self.connection:
                self.sendCommand((msg, None))
        elif msg == 'YOU_ARE_DEAD':
            pass
        elif msg == 'BROADCAST_CHAT':
            self.world.send((self.channel, 'CHAT_TO_ALL', msgArgs[0]))
        elif msg == 'CHAT':
            self.sendCommand((msg, '%d:%s'%(id(sentFrom),msgArgs[0])))
        elif msg == 'BYE':
            self.connection.disconnect()
        else:
            raise UnknownMessageError(msg, sentFrom);
