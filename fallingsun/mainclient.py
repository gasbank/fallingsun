import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from client import SClient

def main():
    random.seed(1)
    
    logging.getLogger().setLevel(logging.INFO)
    
    worldActor = SWorld(width=8, height=8, disableCollisionCheck=True)
    world = worldActor.channel

    client = SClient(world, 'Client', ('14.49.42.133', 3000)).channel
    
    SDisplayWindow(world, windowTitle='Falling Sun Client', client=client)

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
