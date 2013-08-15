import stackless
import random
from world import SWorld
from displaywindow import SDisplayWindow
from home import SHome
from tree import STree
from woodcutter import SWoodcutter

random.seed(1)

totalWood = 0

gWorld = SWorld().channel

SDisplayWindow(gWorld)        

homeList = []
#gatheringList = [ "WOOD", "APPLE" ]
gatheringList = [ "WOOD" ]

for i in range(1):
    loc = (random.randrange(50,450),random.randrange(50,450))
    homeList.append(SHome(gWorld, location=loc, instanceName="Home #%d" % i))

for i in range(20):
    gatheringName = random.choice(gatheringList)
    loc = (random.randrange(50,450),random.randrange(50,450))
    STree(gWorld, gatheringName, location=loc, instanceName="Tree #%d [%s]" % (i, gatheringName))

for i in range(30):
    loc = (random.randrange(50,450),random.randrange(50,450))
    SWoodcutter(gWorld,
                loc,
                homeLocation=random.choice(homeList).location,
                velocity=50+(random.random()-0.5)*3,
                instanceName="Woodcutter #%d" % (i+1)
                )

logFile = open('schedlog.log', 'w')                
                
def schedule_cb(prev, next):
    #logFile.write("SCHEDULE %s --> %s\n" % (prev, next))
    logFile.write("%s\n" % next)

#stackless.set_schedule_callback(schedule_cb)
                
try:
    #stackless.run(100000000, totaltimeout=True)
    stackless.run()
    
except KeyboardInterrupt:
    print "Exit"

print "totalWood=", totalWood
