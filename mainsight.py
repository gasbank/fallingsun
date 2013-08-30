import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey
from sight import SSight
from server import SServer
def main():
    random.seed(1)
    
    logging.getLogger().setLevel(logging.INFO)
    
    worldActor = SWorld(width=10, height=10)
    world = worldActor.channel
    
    SDisplayWindow(world)

    SPrey(world, location=(32 * 0 + 16, 32 * 0 + 16), velocity=20,
          angle=90, instanceName='Prey', stamina=100, maxStamina=100,
          intention='ROAMING')
    
    SSight(world, location=(32 * 5, 32* 5), instanceName='Sight',
           sightRange=2)
    
    SServer(world, 'Server')
        
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
