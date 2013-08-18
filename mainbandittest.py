import stackless  # @UnresolvedImport
import random
import actor
from world import SWorld
from displaywindow import SDisplayWindow
from home import SHome
from woodcutter import SWoodcutter
from bandit import SBandit

def getRandomLoc():
    return (random.randrange(50, 450), random.randrange(50, 450))

def main():
    random.seed(1)

    world = SWorld().channel

    SDisplayWindow(world)        

    home = SHome(world, location=(100,100), instanceName='WoodcutterHome')
    SWoodcutter(world, location=(100,100), homeLocation=home.location, velocity=4, instanceName='Woodcutter', roamingRadius=200, stamina=10, maxStamina=10)

    for i in range(20):
        SWoodcutter(world,
                    location=getRandomLoc(),
                    homeLocation=home.location,
                    velocity=50 + (random.random() - 0.5) * 3,
                    instanceName="Woodcutter #%d" % (i + 1)
                    )
    

    home2 = SHome(world, location=(300,300), instanceName='BanditHome', staminaRefillSpeed=100)
    SBandit(world, location=(300,300), homeLocation=home2.location, velocity=5, instanceName='Bandit')
    
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
