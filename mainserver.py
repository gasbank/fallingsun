#coding:utf-8
import stackless  # @UnresolvedImport
import random
import logging
import weakref
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey
from tree import STree
from server import SServer
from sight import SSight
from home import SHome
from woodcutter import SWoodcutter
from websocketserver import SWebSocketServer
import dialog

def getRandomActorTile(minX, minY, maxX, maxY):
    return tuple(32 * random.randrange(m,M) + 16 for m,M in [(minX, maxX),
                                                             (minY, maxY)])

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
    
    #
    # Initially joining actors
    #
    #STree(world, 'WOOD', location=(32*5+16,32*5+16), instanceName='TestTree')
    STree(world, 'WOOD', location=(32*5+16,32*15+16), instanceName='Tree',
          hitpoints=3, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*11+16,32*7+16),
          instanceName='FarawayTree', hitpoints=4, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*15+16,32*8+16), instanceName='VFTree',
          hitpoints=15, hitpointsDecay=0)
    
    STree(world, 'WOOD', location=(32*6+16,32*5+16),
          instanceName='HiddenTree', hitpoints=7, hitpointsDecay=0)
    
    
    home = SHome(world, location=(32*10+16,32*13+16),
                 instanceName='WoodcutterHome').channel
    SWoodcutter(world, location=(32*0+16, 32*16+16), velocity=20, home=home,
                instanceName='Woodcutter', roamingRadius=200, stamina=10,
                maxStamina=1000, intention='PATHFINDING_HARVESTABLE',
                display=None)
    
    for i in range(10):
        SPrey(world, location=getRandomActorTile(0,0,1,1), velocity=20,
              angle=getRandomAngle(), instanceName='Prey%d'%i, stamina=100,
              maxStamina=100, roamingVelocity=random.randrange(25,35),
              intention='ROAMING')
    
    #
    # Sight
    #
    '''
    sightX, sightY = 14, 14
    sight = SSight(world, location=(32 * sightX, 32 * sightY),
                   instanceName='TestSight', sightRange=7).channel'''
    you = SPrey(world, location=getRandomActorTile(19,6,20,7),
                velocity=20, angle=getRandomAngle(), instanceName='YOU',
                stamina=100, maxStamina=100,
                roamingVelocity=random.randrange(25,35),
                intention='SYNCING').channel

    #
    # 막촌 보좌관
    #
    SPrey(world, location=getRandomActorTile(19,5,20,6), velocity=20,
          angle=180, instanceName='HeadmanAssistant', stamina=100, maxStamina=100,
          roamingVelocity=random.randrange(25,35),
          intention='SYNCING', conversation=dialog.HeadmanAssistant())

    #
    # 평범한 막촌 주민
    #
    SPrey(world, location=getRandomActorTile(19,2,20,3), velocity=20,
          angle=180, instanceName='Villager', stamina=100, maxStamina=100,
          roamingVelocity=random.randrange(25,35),
          intention='SYNCING', conversation=dialog.Villager())

    #
    # Display
    #
    SDisplayWindow(world, windowTitle='Falling Sun Server',
                   swidth=32*23, sheight=32*15, client=you,
                   sightedActorsOnly=False)

    #
    # Servers
    #
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
