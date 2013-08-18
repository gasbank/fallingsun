import stackless  # @UnresolvedImport
import random, unittest
import actor
from world import SWorld
from home import SHome
from woodcutter import SWoodcutter
from tree import STree

def getRandomLoc():
    return (random.randrange(50, 450), random.randrange(50, 450))

class WoodcutterTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def testOneWood(self):
        
        test()
    
def test():
    random.seed(1)
    
    world = SWorld(exitOnNoHavestables=True).channel

    home = SHome(world, location=(100,100), instanceName='WoodcutterHome')
    SWoodcutter(world, location=(100,100), homeLocation=home.location, velocity=4, instanceName='Woodcutter', roamingRadius=200, stamina=10, maxStamina=10)

    tree = STree(world, 'WOOD', location=(150,150), instanceName='Tree')
     
    world.send((None, 'START_TICK_TASKLET'))   
    r = stackless.run()
    print 'End of Program, stackless.run() result =', r
    
    assert tree.hitpoints == 0, 'Tree hit points are not zero, they are %d.' % tree.hitpoints
    
    actor.printAllActorChannelBalances()


        
#test()

#print 'Finished successfully.'
