from actor import SActor, ActorProperties, NamedTasklet
from sight import SSight
import server
import traceback
import cPickle

class SUser(SActor):
    '''
    @property
    def connection(self):
        return self._connection
    '''
    
    def __init__(self, world, instanceName, connection):
        SActor.__init__(self, instanceName)
        self.world = world
        self.connection = connection
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         instanceName=self.instanceName,
                                         physical=False, public=False)))
        
        self.sight = SSight(world, location=(32 * 5, 32* 5),
                            instanceName=instanceName+'Sight',
                            sightRange=3, user=self.channel).channel

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
        except:
            print 'WTF...'
            traceback.print_exc()
        finally:
            if self.connection:
                self.connection.Disconnect()
                self.connection = None

    def HandleCommand(self):
        serverActor = self.connection.serverActor
        
        #self.connection.Write("> ")
        
        line = self.connection.ReadLine()
        
        '''
        words = [ word.strip() for word in line.strip().split(" ") ]
        verb = words[0]

        if verb == "look":
            userList = serverActor.ListUsers()
            self.connection.WriteLine("There are %d users connected:" % len(userList))
            self.connection.WriteLine("Name\tHost\t\tPort")
            self.connection.WriteLine("-" * 40)
            for user in userList:
                host, port = user.connection.clientAddress
                self.connection.WriteLine("Unknown\t"+ str(host) +"\t"+ str(port))
        elif verb == "say":
            line = line[4:]
            secondPartyPrefix = "Someone says: "
            for user in serverActor.ListUsers():
                if user is self:
                    prefix = "You say: "
                else:
                    prefix = secondPartyPrefix
                user.connection.WriteLine(prefix + "\"%s\"" % line)
        elif verb == "quit":
            return False
        elif verb == "help":
            self.connection.WriteLine("Commands:")
            for verb in [ "look", "say", "quit", "help" ]:
                self.connection.WriteLine("  "+ verb)
        elif verb == 'bye':
            self.connection.WriteLine('bye')
        else:
            self.connection.WriteLine("Unknown command.  Type 'help' to see a list of available commands.")
        '''
        return True

    def OnRemoteDisconnection(self):
        self.sight.send((self.channel, 'KILL_YOURSELF'))
        self.info("Disconnected %d (remote)" % id(self))

    def OnUserDisconnection(self):
        self.sight.send((self.channel, 'KILL_YOURSELF'))
        self.info("Disconnected %d (local)" % id(self))
                
    def defaultMessageAction(self, args):
        sentFrom, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            pass
        elif msg == 'SPAWN':
            actors = []
            for na, np in msgArgs[0]:
                p = (id(na), np.name, np.location, np.angle, np.velocity)
                actors.append(p)
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('SPAWN', actors), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        elif msg == 'DESPAWN':
            actors = []
            for na, np in msgArgs[0]:
                actors.append((id(na),))
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('DESPAWN', actors), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        elif msg == 'UPDATE_VECTOR':
            f = self.connection.clientSocket.makefile('wb', 512)
            cPickle.dump(('UPDATE_VECTOR', (id(msgArgs[0]),
                          msgArgs[1].location, msgArgs[1].angle,
                          msgArgs[1].velocity)), f, cPickle.HIGHEST_PROTOCOL)
            f.close()
        else:
            raise RuntimeError("ERROR: Unknown message %s sent from %s"
                               % (msg, sentFrom));
