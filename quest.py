import actor
import weakref

class QuestManager(actor.SActor):
    def __init__(self, world, instanceName='QuestManager'):
        actor.SActor.__init__(self, instanceName)
        self.world = world
        self.world.send((self.channel, 'JOIN',
                         actor.ActorProperties(self.__class__.__name__)))
        

class Quest(object):
    def __init__(self):
        self._tasks = []
        
    def addTask(t):
        self._tasks.append(t)
    
        
class Task(actor.SActor):
    def __init__(self, owner):
        actor.SActor.__init__(self, 'Task')
        self._ownerWr = weakref.ref(owner)

class AcquireItemTask(Task):
    def __init__(self, owner, itemActor):
        Task.__init__(self, owner)
        self._itemActor = itemActor
        
        actor.NamedTasklet(owner.send)((self.channel, 'NEW_TASK', self))
    
    @property
    def isDone(self):
        rch = actor.NamedChannel()
        self._ownerWr().send((self.channel, 'QUERY_HAVE_ITEM', rch,
                              self._itemWr))
        return rch.receive()
        
        