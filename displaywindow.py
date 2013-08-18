from actor import SActor, ActorProperties
import pygame, os

swidth = 500
sheight = 500

class SDisplayWindow(SActor):
    def __init__(self, world):
        SActor.__init__(self)
        self.world = world
        self.icons = {}
        pygame.init()
        
        self.font = pygame.font.SysFont("Gulim", 15)
        
        pygame.display.set_mode((swidth, sheight))
        pygame.display.set_caption("MmoActor")
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         public=False)))
        #print("DisplayWindow created")
        
        grassFile = os.path.join("data", "004-G_Ground02.png")
        
        self.grassSurface = pygame.image.load(grassFile)
        
    def getTaskletName(self):
        return "DisplayWindow"
        
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            #print "Display updated"
            self.updateDisplay(msgArgs)
            pass
        
            
    def getIcon(self, iconName):
        if self.icons.has_key(iconName):
            return self.icons[iconName]
        else:
            iconFile = os.path.join("data", "%s.bmp" % iconName)
            surface = pygame.image.load(iconFile)
            surface.set_colorkey((0xf3, 0x0a, 0x0a))
            self.icons[iconName] = surface
            return surface
        
    def updateDisplay(self, msgArgs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                
                print self.channel, "--APP_EXIT-->", self.world
                #self.world.send((self.channel, "PRINT_INFO"))
                self.world.send((self.channel, "STOP_TICK_LOOP"))
                
        screen = pygame.display.get_surface()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200,200,200))
        screen.blit(background, (0, 0))
        
        
        mapData = [[0,0,0,0,0,0,0,0,0,0,0,0],
                   [0,1,1,1,0,1,0,0,1,0,0,0],
                   [0,0,0,1,0,1,0,0,1,0,0,0],
                   [0,0,0,1,0,0,0,0,1,0,0,0],
                   [0,0,1,1,1,0,0,0,1,0,0,0],
                   [0,0,0,1,0,0,0,0,1,0,0,0],
                   [0,1,1,1,1,1,1,1,1,1,1,0],
                   [0,1,0,0,0,1,0,0,1,0,0,0],
                   [0,1,0,1,1,1,0,0,1,0,0,0],
                   [0,1,0,0,0,1,0,0,1,0,0,0],
                   [0,1,1,1,0,1,0,0,0,0,0,0],
                   [0,1,0,0,1,1,0,0,0,0,0,0],
                   [0,1,1,1,1,1,0,0,0,1,0,0],
                   [0,0,0,1,0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0,0,0,0,0],]
        
        TS = 32    # Tile Size
        STS = 16   # Sub-Tile Size
        
        for i,r in enumerate(mapData):
            for j,c in enumerate(r):
                
                if c == 0:
                    area = (TS*1,TS*0,TS,TS)
                    screen.blit(self.grassSurface, (TS*j,TS*i), area)
                else:
                    neighbors = '%d%d%d%d' % (mapData[i-1][j], mapData[i+1][j], r[j-1], r[j+1])
                    
                    if neighbors == '0000':
                        area = (TS*0,TS*0,TS,TS)
                        screen.blit(self.grassSurface, (TS*j,TS*i), area)
                        
                    # <--->
                    elif neighbors == '1000':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i), (TS*0+STS*0,TS*3+STS*0,STS,STS*2))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i), (TS*2+STS*1,TS*3+STS*0,STS,STS*2))
                    elif neighbors == '0100':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i), (TS*0+STS*0,TS*1+STS*0,STS,STS*2))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i), (TS*2+STS*1,TS*1+STS*0,STS,STS*2))
                    elif neighbors == '1100':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i), (TS*0+STS*0,TS*2+STS*0,STS,STS*2))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i), (TS*2+STS*1,TS*2+STS*0,STS,STS*2))
                        
                    # A
                    # |
                    # |
                    # |
                    # V
                    elif neighbors == '0010':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*2+STS*0,TS*1+STS*0,STS*2,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*2+STS*0,TS*3+STS*1,STS*2,STS))
                    elif neighbors == '0001':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*0+STS*0,TS*1+STS*0,STS*2,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*0+STS*0,TS*3+STS*1,STS*2,STS))
                    elif neighbors == '0011':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*1+STS*0,TS*1+STS*0,STS*2,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*1+STS*0,TS*3+STS*1,STS*2,STS))
                    
                    # <---+
                    #     |
                    #     V
                    elif neighbors == '0110':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*2+STS*0,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*2+STS*0,TS*0+STS*1,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*1+STS*1,STS*1,STS))

                    # +--->
                    # |
                    # V
                    elif neighbors == '0101':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*0+STS*0,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*0+STS*1,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*0+STS*0,TS*1+STS*1,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*0+STS*1,STS*1,STS))###
                        
                    # A
                    # |
                    # +--->
                    elif neighbors == '1001':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*0+STS*0,TS*3+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*0+STS*0,TS*3+STS*1,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*0+STS*1,TS*3+STS*1,STS*1,STS))
                        
                    #     A
                    #     |
                    # <---+
                    elif neighbors == '1010':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*2+STS*0,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*3+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*2+STS*0,TS*3+STS*1,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*3+STS*1,STS*1,STS))
                        
                    
                    #     A
                    #     |
                    # <---+
                    #     |
                    #     V
                    elif neighbors == '1110':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*2+STS*0,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*2+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*2+STS*0,TS*0+STS*1,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*2+STS*1,STS*1,STS))    
                        
                    # A
                    # |
                    # +--->
                    # |
                    # V
                    elif neighbors == '1101':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*0+STS*0,TS*2+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*0+STS*0,TS*2+STS*1,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*0+STS*1,STS*1,STS))###
                    
                    #    A
                    #    |
                    # <--+-->
                    elif neighbors == '1011':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*2+STS*0,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*2+STS*1,TS*0+STS*0,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*1+STS*0,TS*3+STS*1,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*1+STS*1,TS*3+STS*1,STS*1,STS))
                        
                    # <--+-->
                    #    |
                    #    V
                    elif neighbors == '0111':
                        screen.blit(self.grassSurface, (TS*j    ,TS*i    ), (TS*1+STS*0,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i    ), (TS*1+STS*1,TS*1+STS*0,STS*1,STS))
                        screen.blit(self.grassSurface, (TS*j    ,TS*i+STS), (TS*2+STS*0,TS*0+STS*1,STS*1,STS))###
                        screen.blit(self.grassSurface, (TS*j+STS,TS*i+STS), (TS*2+STS*1,TS*0+STS*1,STS*1,STS))###
                        
                    #      A
                    #      |
                    #  <---+--->
                    #      |
                    #      V
                    elif neighbors == '1111':
                        area = (TS*2,TS*0,TS,TS)
                        screen.blit(self.grassSurface, (TS*j,TS*i), area)
                    else:
                        area = (TS*1,TS*2,TS,TS)
                        screen.blit(self.grassSurface, (TS*j,TS*i), area)
                
                 
                            
        """
        screen.blit(self.grassSurface,
                            (16*0, 16*0),
                            (0,32,16*2,16))
        
        screen.blit(self.grassSurface,
                            (16*0, 16*1),
                            (0,32+16*5,16*2,16))
        
        for i in range(7):
            screen.blit(self.grassSurface,
                                (16*(i+2), 16*0),
                                (16*2,16*2,16*2,16))
            
            screen.blit(self.grassSurface,
                                (16*(i+2), 16*1),
                                (16*2,16*7,16*2,16))
            
        
        screen.blit(self.grassSurface,
                            (16*10, 16*0),
                            (16*4,16*2,16*2,16))
        
        screen.blit(self.grassSurface,
                            (16*10, 16*1),
                            (16*4,16*7,16*2,16))
        """
        
        ws = msgArgs[0]
        for _, actorProp in ws.actors:
            itemImage = self.getIcon(actorProp.name)
            itemImage = pygame.transform.rotate(itemImage, -actorProp.angle)
            screen.blit(itemImage, actorProp.location)
            
            label = self.font.render(actorProp.name, 1, (255,0,0))
            screen.blit(label, actorProp.location)
            
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(actorProp.location[0], actorProp.location[1], actorProp.hitpoints, 5))
            
        pygame.display.flip() 
        
        #print("We have",stackless.runcount,"tasklet(s).")
