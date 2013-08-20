import stackless  # @UnresolvedImport
import random, unittest
import actor  # @UnusedImport
from world import SWorld
from home import SHome
from woodcutter import SWoodcutter
from tree import STree
import level

def getRandomLoc():
    return (random.randrange(50, 450), random.randrange(50, 450))

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def testHomelessStarvation(self):
        
        random.seed(1)
    
        worldActor = SWorld() # For debugging use
        world = worldActor.channel
    
        woodcutter = SWoodcutter(world,
                                 location=(100,100), 
                                 velocity=4, 
                                 instanceName='Woodcutter', 
                                 roamingRadius=200, 
                                 stamina=10, 
                                 maxStamina=10)
    
        world.send((None, 'START_TICK_TASKLET'))   
        r = stackless.run()
        print 'End of Program, stackless.run() result =', r
        
        self.assertFalse(worldActor.registeredActors)
        self.assertEqual('STARVATION', woodcutter.deathReason)
    
    def testOneWoodcutterAndOneWood(self):
        
        random.seed(1)
    
        world = SWorld(exitOnNoHavestables=True).channel
    
        home = SHome(world, 
                     location=(100,100), 
                     instanceName='WoodcutterHome')
        
        SWoodcutter(world, 
                    location=(100,100), 
                    homeLocation=home.location, 
                    velocity=4, 
                    instanceName='Woodcutter', 
                    roamingRadius=200, 
                    stamina=10, 
                    maxStamina=10)
    
        tree = STree(world, 'WOOD', location=(150,150), instanceName='Tree')
         
        world.send((None, 'START_TICK_TASKLET'))   
        r = stackless.run()
        print 'End of Program, stackless.run() result =', r
        
        self.assertEqual(0, tree.hitpoints)
        self.assertEqual('DEPLETED', tree.deathReason)
        
    def testTileNeighborhood4(self):
        
        g = level.TileNeighborhood4(3,3,0,0)
        self.assertEqual((0,1), g.next())
        self.assertEqual((1,0), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,1,0)
        self.assertEqual((1,1), g.next())
        self.assertEqual((0,0), g.next())
        self.assertEqual((2,0), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,2,0)
        self.assertEqual((2,1), g.next())
        self.assertEqual((1,0), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,0,1)
        self.assertEqual((0,0), g.next())
        self.assertEqual((0,2), g.next())
        self.assertEqual((1,1), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,1,1)
        self.assertEqual((1,0), g.next())
        self.assertEqual((1,2), g.next())
        self.assertEqual((0,1), g.next())
        self.assertEqual((2,1), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,2,1)
        self.assertEqual((2,0), g.next())
        self.assertEqual((2,2), g.next())
        self.assertEqual((1,1), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,0,2)
        self.assertEqual((0,1), g.next())
        self.assertEqual((1,2), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,1,2)
        self.assertEqual((1,1), g.next())
        self.assertEqual((0,2), g.next())
        self.assertEqual((2,2), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,2,2)
        self.assertEqual((2,1), g.next())
        self.assertEqual((1,2), g.next())
        self.assertRaises(StopIteration, g.next)
        
        g = level.TileNeighborhood4(3,3,3,3)
        self.assertRaises(StopIteration, g.next)

    def testPathfind(self):
        
        tileData = level.TileLevel()
        
        # Map: 1x1 (No obstacle)
        tileData.terrain = [[0]]
        tileData.building = [[0]]
        tileData.collision = [[0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0)], tileData.findPath(0,0,0,0))
        self.assertRaises(IndexError, tileData.findPath, 0, 0, 1, 1)
        
        # Map: 2x1 (No obstacle)
        tileData.terrain = [[0,0]]
        tileData.building = [[0,0]]
        tileData.collision = [[0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(1,0)], tileData.findPath(0,0,1,0))
        self.assertEqual([(1,0),(0,0)], tileData.findPath(1,0,0,0))
        
        # Map: 3x1 (No obstacle)        
        tileData.terrain = [[0,0,0]]
        tileData.building = [[0,0,0]]
        tileData.collision = [[0,0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(1,0),(2,0)], tileData.findPath(0,0,2,0))
        self.assertEqual([(2,0),(1,0),(0,0)], tileData.findPath(2,0,0,0))
        
        # Map: 3x1
        tileData.terrain = [[0,0,1]]
        tileData.building = [[0,0,1]]
        tileData.collision = [[0,0,1]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(1,0)], tileData.findPath(0,0,1,0))
        self.assertEqual([(1,0),(0,0)], tileData.findPath(1,0,0,0))
        
        # Map: 3x1
        tileData.terrain = [[1,0,0]]
        tileData.building = [[1,0,0]]
        tileData.collision = [[1,0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(1,0),(2,0)], tileData.findPath(1,0,2,0))
        self.assertEqual([(2,0),(1,0)], tileData.findPath(2,0,1,0))
        
        # Map: 3x1 (Unreachable)
        tileData.terrain = [[0,1,0]]
        tileData.building = [[0,1,0]]
        tileData.collision = [[0,1,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([], tileData.findPath(0,0,2,0))
        self.assertEqual([], tileData.findPath(2,0,0,0))
        
        # Map: 2x2 (No obstacle)
        tileData.terrain = [[0,0],
                            [0,0]]
        tileData.building = [[0,0],
                             [0,0]]
        tileData.collision = [[0,0],
                              [0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(1,0)], tileData.findPath(0,0,1,0))
        self.assertEqual([(1,0),(0,0)], tileData.findPath(1,0,0,0))
        self.assertEqual([(0,1),(1,1)], tileData.findPath(0,1,1,1))
        self.assertEqual([(1,1),(0,1)], tileData.findPath(1,1,0,1))
        self.assertEqual([(0,0),(0,1)], tileData.findPath(0,0,0,1))
        self.assertEqual([(1,0),(1,1)], tileData.findPath(1,0,1,1))
        
        # Map: 2x2
        tileData.terrain = [[0,1],
                            [0,0]]
        tileData.building = [[0,1],
                             [0,0]]
        tileData.collision = [[0,1],
                              [0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(0,1),(1,1)], tileData.findPath(0,0,1,1))
        
        # Map: 3x2
        tileData.terrain = [[0,1,0],
                            [0,0,0]]
        tileData.building = [[0,1,0],
                             [0,0,0]]
        tileData.collision = [[0,1,0],
                              [0,0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(0,1),(1,1),(2,1),(2,0)], tileData.findPath(0,0,2,0))
        
        # Map: 3x3
        tileData.terrain = [[0,1,0],
                            [0,0,0],
                            [0,1,0]]
        tileData.building = [[0,1,0],
                             [0,0,0],
                             [0,1,0]]
        tileData.collision = [[0,1,0],
                              [0,0,0],
                              [0,1,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(0,1),(1,1),(2,1),(2,2)], tileData.findPath(0,0,2,2))
        
        # Map: 3x3
        tileData.terrain = [[0,0,0],
                            [0,1,0],
                            [0,1,1]]
        tileData.building = [[0,0,0],
                             [0,1,0],
                             [0,1,1]]
        tileData.collision = [[0,0,0],
                              [0,1,0],
                              [0,1,1]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,2),(0,1),(0,0),(1,0),(2,0),(2,1)], tileData.findPath(0,2,2,1))
        
        
    @unittest.expectedFailure
    def testPathfindNotGuaranteeShortest(self):
        
        tileData = level.TileLevel()
        
        # Map: 4x3
        tileData.terrain = [[0,0,0,0],
                            [0,1,1,0],
                            [0,0,0,0]]
        tileData.building = [[0,0,0,0],
                             [0,1,1,0],
                             [0,0,0,0]]
        tileData.collision = [[0,0,0,0],
                              [0,1,1,0],
                              [0,0,0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(1,0),(0,0),(1,0),(2,0),(2,1)], tileData.findPath(1,0,1,2))
        
        