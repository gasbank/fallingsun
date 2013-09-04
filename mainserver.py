import stackless  # @UnresolvedImport
import random
import logging
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey
from tree import STree
from server import SServer
from sight import SSight
from websocketserver import SWebSocketServer

def getRandomActorTile(maxX, maxY):
    return tuple(32 * random.randrange(0,v) + 16 for v in [maxX, maxY])

def getRandomAngle():
    return random.choice([0,90,180,270])

def main():
    random.seed(1)
    
    logging.getLogger().setLevel(logging.INFO)
    
    worldSizeX=15
    worldSizeY=15
    worldActor = SWorld(width=worldSizeX, height=worldSizeY,
                        disableCollisionCheck=True, useTestData=True)
    world = worldActor.channel
    
    sightX, sightY = 5, 5
    sight = SSight(world, location=(32 * sightX, 32 * sightY),
                   instanceName='TestSight', sightRange=5).channel

    SDisplayWindow(world, windowTitle='Falling Sun Server',
                   swidth=32*15, sheight=32*15, client=sight)
    
    STree(world, 'WOOD', location=(32*5,32*5), instanceName='TestTree')

    for i in range(8):
        SPrey(world, location=getRandomActorTile(worldSizeX, worldSizeY),
              velocity=20, angle=getRandomAngle(), instanceName='Prey%d'%i,
              stamina=100, maxStamina=100,
              roamingVelocity=random.randrange(25,35), intention='SYNCING')
    
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
