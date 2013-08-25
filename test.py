import stackless  # @UnresolvedImport
import random
import unittest
import logging
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
    
    def tick(self, world):
        logging.debug('Tick!')
        world.send((None, 'START_SINGLE_TICK_TASKLET'))
        self.assertIsNone(stackless.run())
    
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
        logging.info('End of Program, stackless.run() result = %s' % r)
        
        self.assertEqual('STARVATION', woodcutter.deathReason)
        self.assertFalse(worldActor.registeredActors)
        self.assertFalse(worldActor.aboutToBeKilledActors)
        self.assertFalse(worldActor.tickDisabledActors)
        
    def testTeleport(self):
    
        random.seed(1)
        
        worldActor = SWorld() # For debugging use
        world = worldActor.channel
    
        location0 = (32*3+16,32*3+16)
        wc = SWoodcutter(world, location=location0, velocity=0,
                         instanceName='Woodcutter', roamingRadius=200, 
                         stamina=10, maxStamina=100, intention='RESTING')
    
        self.tick(world)
        self.assertEqual('RESTING', wc.intention)
        self.assertEqual(location0, wc.location)
        
        location1 = (32*7+16,32*7+16)
        worldActor.teleportActor(wc.channel, location1)
        self.tick(world)
        self.assertEqual('RESTING', wc.intention)
        self.assertEqual(location1, wc.location)
        
    def testEnterLeave(self):
        
        logging.getLogger().setLevel(logging.DEBUG)
        
        random.seed(1)
        
        worldActor = SWorld() # For debugging use
        world = worldActor.channel
    
        wcLoc0 = (32*3+16,32*3+16)
        wc = SWoodcutter(world, location=wcLoc0, velocity=0,
                         instanceName='Woodcutter', roamingRadius=200, 
                         stamina=10, maxStamina=100, intention='RESTING')
    
        homeLoc0 = (32*8,32*8)
        home = SHome(world, location=homeLoc0, instanceName='WoodcutterHome')
        
        wcNb = wc.neighbors
        homeNb = home.neighbors
        self.assertEqual([], wcNb)
        self.assertEqual([], homeNb)
        
        self.tick(world)
        self.assertEqual([], wcNb)
        self.assertEqual([], homeNb)
        
        wcLoc1 = (32*8+16,32*9+16)
        worldActor.teleportActor(wc.channel, wcLoc1)
        self.tick(world)
        self.assertEqual([home.channel], wcNb)
        self.assertEqual([wc.channel], homeNb)
        
        wcLoc2 = (32*9+16,32*8+16)
        worldActor.teleportActor(wc.channel, wcLoc2)
        self.tick(world)
        self.assertEqual([home.channel], wcNb)
        self.assertEqual([wc.channel], homeNb)
        
        wcLoc3 = (32*9+16+5,32*8+16+5)
        worldActor.teleportActor(wc.channel, wcLoc3)
        self.tick(world)
        self.assertEqual([home.channel], wcNb)
        self.assertEqual([wc.channel], homeNb)
        
        wcLoc4 = (32*9+16+5+32,32*8+16+5+32)
        worldActor.teleportActor(wc.channel, wcLoc4)
        self.tick(world)
        self.assertEqual([], wcNb)
        self.assertEqual([], homeNb)
        
        wcLoc5 = (32*1+16,32*2+16)
        worldActor.teleportActor(wc.channel, wcLoc5)
        self.tick(world)
        self.assertEqual([], wcNb)
        self.assertEqual([], homeNb)
        
    def testWoodcutterAddStamina(self):
        
        random.seed(1)
    
        worldActor = SWorld() # For debugging use
        world = worldActor.channel
    
        woodcutter = SWoodcutter(world, location=(32*6+16,32*4+16), velocity=4, 
                                 instanceName='Woodcutter', roamingRadius=200, 
                                 stamina=0, maxStamina=10)
    
        SHome(world, location=(32*6,32*3), instanceName='WoodcutterHome')
        
        world.send((None, 'START_SINGLE_TICK_TASKLET'))   
        r = stackless.run()
        logging.info('End of Program, stackless.run() result = %s' % r)
        
        self.assertGreater(woodcutter.stamina, 0)
        
    def testOneWoodcutterAndOneWood(self):
        
        '''
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Debug level logging enabled.')
        '''
        
        random.seed(1)
    
        world = SWorld(exitOnNoHarvestables=True).channel
    
        home = SHome(world, 
                     location=(32*5,32*5), 
                     instanceName='WoodcutterHome')
        
        SWoodcutter(world, 
                    location=(32*3+16,32*3+16), 
                    homeLocation=home.location, 
                    velocity=4, 
                    instanceName='Woodcutter', 
                    roamingRadius=200, 
                    stamina=10000,
                    maxStamina=10000,
                    intention='PATHFINDING_HARVESTABLE')
    
        tree = STree(world, 'WOOD', location=(32*4,32*3), instanceName='Tree',
                     hitpoints=1)
         
        world.send((None, 'START_TICK_TASKLET'))   
        r = stackless.run()
        logging.info('End of Program, stackless.run() result = %s' % r)
        
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
        
        # Map: 1x1 (JAMMED!)
        tileData.terrain = [[1]]
        tileData.building = [[1]]
        tileData.collision = [[1]]
        tileData.updateLevelSize()
        
        self.assertEqual([], tileData.findPath(0,0,0,0))
        
        # Map: 2x1 (No obstacle)
        tileData.terrain = [[0,0]]
        tileData.building = [[0,0]]
        tileData.collision = [[0,0]]
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0)], tileData.findPath(0,0,0,0))
        self.assertEqual([(1,0)], tileData.findPath(1,0,1,0))
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
        
        self.assertEqual([(0,0)], tileData.findPath(0,0,2,0))
        self.assertEqual([(2,0)], tileData.findPath(2,0,0,0))
        self.assertEqual([], tileData.findPath(1,0,0,0)) # Jammed
        self.assertEqual([], tileData.findPath(1,0,2,0)) # Jammed
        
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
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        self.assertEqual([(1,0),(0,0),(1,0),(2,0),(2,1)], tileData.findPath(1,0,1,2))
        
    def testPathfindGoalCellIsNotMovable(self):
        
        tileData = level.TileLevel()
        
        # Map: 2x1 (Cannot move, stay still)
        tileData.terrain = [[0,1]]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0)], tileData.findPath(0,0,1,0))
        
        # Map: 3x1 (Cannot reach the destination)
        tileData.terrain = [[0,0,1]]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(1,0)], tileData.findPath(0,0,2,0))
        self.assertEqual([(1,0)], tileData.findPath(1,0,2,0))
    
    def testPathfindGoalCellIsNotMovable2(self):
        
        tileData = level.TileLevel()
        
        # Map: 3x3 (Cannot reach the destination)
        tileData.terrain = [[0,1,1],
                            [0,0,1],
                            [1,1,1]]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(0,1),(1,1)], tileData.findPath(0,0,2,2))
        
        # Map: 3x3 (Cannot reach the destination)
        tileData.terrain = [[0,1,1],
                            [0,0,0],
                            [1,1,1]]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        self.assertEqual([(0,0),(0,1),(1,1),(2,1)], tileData.findPath(0,0,2,2))
        self.assertEqual([(0,0),(0,1),(1,1),(2,1)], tileData.findPath(0,0,2,0))
        
        # Map: 3x3 (Cannot reach the destination)
        tileData.terrain = [[1,1,1],
                            [1,0,1],
                            [1,1,1]]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        for i in range(3):
            for j in range(3):
                self.assertEqual([(1,1)], tileData.findPath(1,1,i,j))
        
        # Map: 4x4 (Cannot reach the destination)
        tileData.terrain = [[1,1,1,0],
                            [1,0,1,0],
                            [1,1,1,0],
                            [0,0,0,0],]
        tileData.building = tileData.collision = tileData.terrain
        tileData.updateLevelSize()
        
        for i in range(4):
            for j in range(4):
                self.assertEqual([(1,1)], tileData.findPath(1,1,i,j))
                
        self.assertEqual([(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0)],
                         tileData.findPath(0,3,3,0))
    
        self.assertEqual([(0,3)], tileData.findPath(0,3,0,2))
        
        
        
        