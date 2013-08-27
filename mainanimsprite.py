import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey
from tree import STree
from woodcutter import SWoodcutter
from home import SHome

def main():
    random.seed(1)
    
    #world = SWorld(disableCollisionCheck=True).channel
    world = SWorld(useTestData=True).channel

    display = SDisplayWindow(world).channel
    
    '''
    for i in range(10):
        SPrey(world,
              location=(32*11+16,32*8+16),
              velocity=10,
              angle=90,
              instanceName='PreyI #%d' % (i+1),
              stamina=100,
              maxStamina=100,
              intention='RESTING')
        
    for i in range(10):
        SPrey(world,
              location=(32*5+16,32*5+16),
              velocity=5,
              angle=90,
              instanceName='Prey II #%d' % (i+1),
              stamina=100,
              maxStamina=100,
              intention='RESTING')
    '''
    
    
    SPrey(world, location=(32*5+16,32*5+16), velocity=50, angle=90,
          instanceName='Prey', stamina=100, maxStamina=100, intention='ROAMING')
    
    
    
    logging.getLogger().setLevel(logging.INFO)
    #logging.debug('Debug level logging enabled.')
    
     
    STree(world, 'WOOD', location=(32*5,32*15), instanceName='Tree',
          hitpoints=3, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*11,32*7), instanceName='FarawayTree',
          hitpoints=4, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*15,32*8), instanceName='VFTree',
          hitpoints=15, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*6,32*5), instanceName='HiddenTree',
          hitpoints=7, hitpointsDecay=0)
    
    home = SHome(world, location=(32*10,32*13), instanceName='WoodcutterHome')
    
    home2 = SHome(world, location=(32*16,32*17), instanceName='Wc2Home')
    
    wc = SWoodcutter(world, location=(32*0+16,32*16+16),
                     homeLocation=home.location, velocity=20,
                     home=home.channel,
                     instanceName='Woodcutter', roamingRadius=200, 
                     stamina=10, maxStamina=1000,
                     intention='PATHFINDING_HARVESTABLE',
                     display=display)
    
    SWoodcutter(world, location=(32*0+16,32*2+16),
                     homeLocation=home2.location, velocity=20,
                     home=home2.channel,
                     instanceName='Wc2', roamingRadius=200, 
                     stamina=10, maxStamina=1000,
                     intention='PATHFINDING_HARVESTABLE',
                     display=display)
    
    SWoodcutter(world, location=(32*16+16,32*18+16),
                     homeLocation=home2.location, velocity=20,
                     home=home2.channel,
                     instanceName='Wc3-rest', roamingRadius=200, 
                     stamina=6, maxStamina=10,
                     intention='RESTING',
                     display=display)
    
    logging.info('All actors initialized successfully.')
    logging.info('Starting the tick tasklet...')
    
    try:
        world.send((None, 'START_TICK_TASKLET'))
        r = stackless.run()
        assert r is None
        
    except KeyboardInterrupt:
        logging.info('Exit by KeyboardInterrupt')

    logging.info('End of Program')
        
if __name__ == '__main__':
    main()
