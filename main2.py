import stackless  # @UnresolvedImport
import random
import actor
from world import SWorld
from displaywindow import SDisplayWindow
from home import SHome
from tree import STree
from woodcutter import SWoodcutter

def main():
    random.seed(1)

    world = SWorld().channel

    SDisplayWindow(world)        

    home = SHome(world, location=(250,400), instanceName='Home')
    STree(world, 'WOOD', location=(50,50), instanceName='FarawayTree', hitpoints=1)
    STree(world, 'WOOD', location=(260,410), instanceName="Tree", hitpoints=1)
    SWoodcutter(world,
                location=(200,400),
                homeLocation=home.location,
                velocity=50,
                instanceName='Woodcutter'
                )

    try:
        actor.printAllActorChannelBalances()
        r = stackless.run()
        print 'stackless.run() result =', r
        
    except KeyboardInterrupt:
        print "Exit"

    print "End of Program"
    
    actor.printAllActorChannelBalances()
        
if __name__ == '__main__':
    main()
