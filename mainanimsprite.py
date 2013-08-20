import stackless  # @UnresolvedImport
import random
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey

def main():
    random.seed(1)
    
    world = SWorld(disableCollisionCheck=True).channel

    SDisplayWindow(world)
    
    
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
    
    
    SPrey(world,
          location=(32*5+16,32*5+16),
          velocity=50,
          angle=90,
          instanceName='Prey',
          stamina=100,
          maxStamina=100,
          intention='ROAMING')
    
    print 'Actors initialized.'
    
    try:
        world.send((None, 'START_TICK_TASKLET'))
        r = stackless.run()
        print 'stackless.run() result =', r
        
    except KeyboardInterrupt:
        print "Exit"

    print "End of Program"
        
if __name__ == '__main__':
    main()
