import stackless  # @UnresolvedImport
import random
import actor
from world import SWorld
from displaywindow import SDisplayWindow
from home import SHome
from tree import STree
from woodcutter import SWoodcutter
from architect import SArchitect

def getRandomLoc():
    return (random.randrange(50, 450), random.randrange(50, 450))

def main():
    random.seed(1)

    totalWood = 0

    world = SWorld().channel

    SDisplayWindow(world)        

    homeList = []
    gatheringList = [ "WOOD" ]

    for i in range(1):
        homeList.append(SHome(world, location=getRandomLoc(), instanceName="Home #%d" % (i + 1)))
        #homeList.append(SHome(world, location=(250,400), instanceName="Home #%d" % (i + 1)))

    for i in range(20):
        gatheringName = random.choice(gatheringList)
        STree(world, gatheringName, location=getRandomLoc(), instanceName="Tree #%d [%s]" % (i + 1, gatheringName), hitpoints=10)

    for i in range(20):
        SWoodcutter(world,
                    location=getRandomLoc(),
                    homeLocation=random.choice(homeList).location,
                    velocity=50 + (random.random() - 0.5) * 3,
                    instanceName="Woodcutter #%d" % (i + 1)
                    )

    homeLoc = random.choice(homeList).location
    SArchitect(world,
               location=homeLoc,
               homeLocation=homeLoc,
               velocity=50 + (random.random() - 0.5) * 3,
               instanceName="Architect"
               )


    try:
        actor.printAllActorChannelBalances()
        r = stackless.run()
        print 'stackless.run() result =', r
        
    except KeyboardInterrupt:
        print "Exit"

    print "End of Program", totalWood
    
    actor.printAllActorChannelBalances()
        
if __name__ == '__main__':
    main()
    
