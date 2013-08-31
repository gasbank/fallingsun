import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from client import SClient
#from blank import SBlank

def main():
    random.seed(1)
    
    logging.getLogger().setLevel(logging.INFO)
    
    worldActor = SWorld(width=10, height=10)
    world = worldActor.channel
    
    SDisplayWindow(world, windowTitle='Falling Sun Client')

    SClient(world, 'Client', ('127.0.0.1', 3000))
    
    #SBlank(world, 'SPrey', (32*5,32*5), 'TestBlank')
        
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
