import stackless  # @UnresolvedImport
import random, unittest
import actor  # @UnusedImport
from world import SWorld
from home import SHome
from woodcutter import SWoodcutter
from tree import STree

def getRandomLoc():
    return (random.randrange(50, 450), random.randrange(50, 450))

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def testHomelessStarvation(self):
        
        random.seed(1)
    
        worldActor = SWorld() # For debugging use
        world = worldActor.channel
    
        woodcutter = SWoodcutter(world, location=(100,100), velocity=4, instanceName='Woodcutter', roamingRadius=200, stamina=10, maxStamina=10)
    
        world.send((None, 'START_TICK_TASKLET'))   
        r = stackless.run()
        print 'End of Program, stackless.run() result =', r
        
        self.assertFalse(worldActor.registeredActors)
        self.assertEqual('STARVATION', woodcutter.deathReason)
    
    def testOneWoodcutterAndOneWood(self):
        
        random.seed(1)
    
        world = SWorld(exitOnNoHavestables=True).channel
    
        home = SHome(world, location=(100,100), instanceName='WoodcutterHome')
        SWoodcutter(world, location=(100,100), homeLocation=home.location, velocity=4, instanceName='Woodcutter', roamingRadius=200, stamina=10, maxStamina=10)
    
        tree = STree(world, 'WOOD', location=(150,150), instanceName='Tree')
         
        world.send((None, 'START_TICK_TASKLET'))   
        r = stackless.run()
        print 'End of Program, stackless.run() result =', r
        
        self.assertEqual(0, tree.hitpoints)
        self.assertEqual('DEPLETED', tree.deathReason)
