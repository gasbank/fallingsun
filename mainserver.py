import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey
from server import SServer
from websocketserver import SWebSocketServer

def main():
    random.seed(1)
    
    logging.getLogger().setLevel(logging.INFO)
    
    worldActor = SWorld(width=8, height=8, disableCollisionCheck=True)
    world = worldActor.channel
    
    SDisplayWindow(world, windowTitle='Falling Sun Server')

    for i in range(500):
        SPrey(world, location=(32 * 0 + 16, 32 * 0 + 16), velocity=20,
              angle=90, instanceName='Prey%d'%i, stamina=100, maxStamina=100,
              intention='ROAMING')
    
    SServer(world, 'Server')
    SWebSocketServer(world, 'WebSocketServer')
        
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
