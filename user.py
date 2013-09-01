from actor import SActor, ActorProperties, NamedTasklet, UnknownMessageError, UnauthorizedAccessError
from prey import SPrey
from sight import SSight
import server
import cPickle
import socket

class SUser(SActor):
    
    def __init__(self, world, instanceName, connection):
        SActor.__init__(self, instanceName)
        self.world = world
        self.connection = connection
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))
        
        sightX, sightY = 5, 5
        self.sight = SSight(world, location=(32 * sightX, 32* sightY),
                            instanceName=instanceName+'Sight',
                            sightRange=3, user=self.channel).channel
        
        self.pawn = SPrey(world, location=(32*sightX+16,32*sightY+16),
                          velocity=0, angle=90,
                          instanceName=self.instanceName+'Pawn', stamina=100,
                          maxStamina=100, intention='SYNCING').channel
                          
        f = self.connection.clientSocket.makefile('wb', 512)
        cPickle.dump(('OWNERSHIP', id(self.pawn)), f,
                     cPickle.HIGHEST_PROTOCOL)
        f.close()

        # The tasklet will hold a reference to the user keeping the instance
        # alive as long as it is handling commands.
        NamedTasklet(self.Run)()

    def Run(self):
        serverActor = self.connection.serverActor

        # Notify the server that a user is connected.
        serverActor.RegisterUser(self)
        self.info("Connected %d from %s" % (id(self), self.connection.clientAddress))

        try:
            while self.HandleCommand():
                pass

            self.OnUserDisconnection()
        except server.RemoteDisconnectionError:
            #print 'remotedisconnectionerror caught'
            self.OnRemoteDisconnection()
            #print 'before set connection to None'
            self.connection = None
            #print 'after set connection to None'
            '''except:
            print 'WTF...'
            traceback.print_exc()'''
        finally:
            if self.connection:
                self.connection.Disconnect()
                self.connection = None
            
    def HandleCommand(self):
        try:
            f = self.connection.clientSocket.makefile('rb', 512)
            cmd, cmdArgs = cPickle.load(f)
            f.close()
        except socket.error:
            raise server.RemoteDisconnectionError
        except EOFError:
            return False
        
        try:
            self.processMessageMethod((self.connection, cmd, cmdArgs))
        except UnauthorizedAccessError, e:
            self.warn(e)
        
        return True

    def OnRemoteDisconnection(self):
        self.world.send_sequence([(self.sight, 'KILLME'),
                                  (self.pawn, 'KILLME')])
        self.info("Disconnected %d (remote)" % id(self))

    def OnUserDisconnection(self):
        self.world.send_sequence([(self.sight, 'KILLME'),
                                  (self.pawn, 'KILLME')])
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
                name = 'SHeadman' if na is self.pawn else np.name
                #name = np.name  
                p = (id(na), name, np.location, np.angle, np.velocity)
                actors.append(p)
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('SPAWN', actors), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        elif msg == 'SEND_DESPAWN':
            if not self.connection:
                return
            
            actors = []
            for na, np in msgArgs[0]:
                actors.append((id(na),))
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('DESPAWN', actors), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        elif msg == 'SEND_UPDATE_VECTOR':
            if not self.connection:
                return
            
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('UPDATE_VECTOR', (id(msgArgs[0]),
                          msgArgs[1].location, msgArgs[1].angle,
                          msgArgs[1].velocity)), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        elif msg == 'UPDATE_VECTOR':
            actorId, (angle, velocity) = msgArgs[0]
            
            if sentFrom is self.connection:
                if id(self.pawn) != actorId:
                    raise UnauthorizedAccessError(msg, sentFrom)
            
                self.world.send((self.pawn, 'UPDATE_VECTOR', angle, velocity))
                
        elif msg == 'CLOSE_SOCKET':
            if self.connection:
                f = self.connection.clientSocket.makefile('wb', 512)
                cPickle.dump((msg, None), f, cPickle.HIGHEST_PROTOCOL)
                f.close()
                
        else:
            raise UnknownMessageError(msg, sentFrom);
