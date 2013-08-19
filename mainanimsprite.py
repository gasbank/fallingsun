import stackless  # @UnresolvedImport
import random
from world import SWorld
from displaywindow import SDisplayWindow
from prey import SPrey

def main():
    random.seed(1)
    
    world = SWorld().channel

    SDisplayWindow(world)        
    
    
    SPrey(world,
          location=(32*5,32*5),
          velocity=10,
          angle=90,
          instanceName='Prey',
          stamina=100,
          maxStamina=100,
          intention='ROAMING')
    
    try:
        world.send((None, 'START_TICK_TASKLET'))
        r = stackless.run()
        print 'stackless.run() result =', r
        
    except KeyboardInterrupt:
        print "Exit"

    print "End of Program"
        
if __name__ == '__main__':
    main()
