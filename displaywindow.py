from actor import SActor, ActorProperties
import pygame, os, logging

swidth = 500
sheight = 500

class SDisplayWindow(SActor):
    def __init__(self, world):
        SActor.__init__(self)
        self.frame = 0
        self.world = world
        self.icons = {}
        pygame.init()
        
        self.font = pygame.font.SysFont("Gulim", 20)
        
        pygame.display.set_mode((swidth, sheight))
        pygame.display.set_caption("MmoActor")
        # print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         public=False)))
        
        self.dustRoadTile = pygame.image.load(os.path.join('data', '004-G_Ground02.png'))
        self.waterTile = pygame.image.load(os.path.join('data', '001-G_Water01.png'))
        self.grasslandTile = pygame.image.load(os.path.join('data', '001-Grassland01.png'))
        self.fighterTile = pygame.image.load(os.path.join('data', '001-Fighter01.png'))
        
        logging.info('The display actor created.')        
        
    def getTaskletName(self):
        return "DisplayWindow"
    
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        if msg == "WORLD_STATE":
            # print "Display updated"
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
    
    def drawTerrainTiles(self, screen, ws):
        
        TS = 32  # Tile Size
        STS = 16  # Sub-Tile Size
        
        animFrame = (self.frame / 80) % 4
        
        for i, r in enumerate(ws.tileData.terrain):
            for j, c in enumerate(r):
                
                if c == 0:
                    area = (TS * 1, TS * 0, TS, TS)
                    screen.blit(self.waterTile, (TS * j, TS * i), area)
                else:
                    neighbors = '%d%d%d%d' % (ws.tileData.terrain[i - 1][j], ws.tileData.terrain[i + 1][j], r[j - 1], r[j + 1])
                    
                    if neighbors == '0000':
                        area = (TS * 0, TS * 0, TS, TS)
                        screen.blit(self.waterTile, (TS * j, TS * i), area)
                        
                    # <--->
                    elif neighbors == '1000':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS, STS * 2))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS, STS * 2))
                    elif neighbors == '0100':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS, STS * 2))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS, STS * 2))
                    elif neighbors == '1100':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS, STS * 2))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS, STS * 2))
                        
                    # A
                    # |
                    # |
                    # |
                    # V
                    elif neighbors == '0010':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
                    elif neighbors == '0001':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
                    elif neighbors == '0011':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
                    
                    # <---+
                    #     |
                    #     V
                    elif neighbors == '0110':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 1, STS * 1, STS))

                    # +--->
                    # |
                    # V
                    elif neighbors == '0101':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 1, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
                        
                    # A
                    # |
                    # +--->
                    elif neighbors == '1001':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
                        
                    #     A
                    #     |
                    # <---+
                    elif neighbors == '1010':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
                        
                    
                    #     A
                    #     |
                    # <---+
                    #     |
                    #     V
                    elif neighbors == '1110':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 1, STS * 1, STS))    
                        
                    # A
                    # |
                    # +--->
                    # |
                    # V
                    elif neighbors == '1101':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 1, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
                    
                    #    A
                    #    |
                    # <--+-->
                    elif neighbors == '1011':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
                        
                    # <--+-->
                    #    |
                    #    V
                    elif neighbors == '0111':
                        screen.blit(self.waterTile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
                        screen.blit(self.waterTile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
                        screen.blit(self.waterTile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
                        
                    #      A
                    #      |
                    #  <---+--->
                    #      |
                    #      V
                    elif neighbors == '1111':
                        area = (TS * 2, TS * 0, TS, TS)
                        screen.blit(self.waterTile, (TS * j, TS * i), area)
                    else:
                        area = (TS * 1, TS * 2, TS, TS)
                        screen.blit(self.waterTile, (TS * j, TS * i), area)
    
    
    def drawBuildingTiles(self, screen, ws):
        
        TS = 32  # Tile Size
        STS = 16  # Sub-Tile Size
        animFrame = 0
        
        for i, r in enumerate(ws.tileData.building):
            for j, c in enumerate(r):
                
                if c == 2:
                    screen.blit(self.grasslandTile, (TS * j      , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 13 + STS * 0, TS * 5, TS * 5))
                elif c == 3:
                    screen.blit(self.grasslandTile, (TS * j - STS, TS * i), (0 * TS * animFrame + TS * 0 + STS * 0, TS * 5 + STS * 0, TS * 4, TS * 5))
                    
    
    def drawCollisionTiles(self, screen, ws):
        
        TS = 32  # Tile Size

        for i, r in enumerate(ws.tileData.collision):
            for j, c in enumerate(r):
                if c != 0 or ws.tileData.terrain[i][j] != 0:
                    pygame.draw.rect(screen, (255, 128, 0),
                                     pygame.Rect(TS*j, TS*i, TS, TS), 1)
        
    def drawPathFindTest(self, screen, ws):
        
        TS = 32  # Tile Size
        path = ws.tileData.findPath(5,5,2,7)
        
        for i, p in enumerate(path):
            
            label = self.font.render("%d"%(i), 1, (0, 0, 255))
            screen.blit(label, (TS*p[0], TS*p[1]))
            pygame.draw.rect(screen, (0, 0, 0),
                             pygame.Rect(TS*p[0], TS*p[1], TS, TS), 2)
            
    def getDirectionFromAngle(self, angle):
        
        SOUTH = 0
        WEST = 1
        EAST = 2
        NORTH = 3
        
        if angle < 0:
            angle += 360
        
        # South -> West -> East -> North
        if 45*1 <= angle < 45*3:
            return EAST
        elif 45*3 <= angle < 45*5:
            return SOUTH
        elif 45*5 <= angle < 45*7:
            return WEST
        else:
            return NORTH
        
        
    def drawAnimatedCharacterSprite(self, screen, actorProp):
        
        TS = 32  # Tile Size
        STS = 16  # Sub-Tile Size
        
        i = actorProp.location[0] / TS
        j = actorProp.location[1] / TS
        
        animFrame = (actorProp.velocity * self.frame / 200) % 4
        direction = self.getDirectionFromAngle(actorProp.angle)
        
        screen.blit(self.fighterTile,
                    (TS * i,
                     TS * j - STS), 
                    (1 * TS * animFrame + TS * 0 + STS * 0,
                     (TS * 1 + STS * 1) * direction,
                     TS * 1,
                     TS * 1 + STS))
        
    def drawActor(self, screen, actorProp):
        
        if actorProp.animatedSprite:
            
            if actorProp.name == '001-Fighter01':
                itemImage = self.fighterTile
            else:
                raise RuntimeError('Not available for the moment.')
            
            self.drawAnimatedCharacterSprite(screen, actorProp)
            
        else:
        
            itemImage = self.getIcon(actorProp.name)
            itemImage = pygame.transform.rotate(itemImage, -actorProp.angle)
            screen.blit(itemImage, actorProp.location)
            
        # Draw the instance name of the actor
        label = self.font.render(actorProp.name, 1, (255, 0, 0))
        screen.blit(label, actorProp.location)

            
        # The hitpoints gauge
        pygame.draw.rect(screen, (0, 255, 0),
                         pygame.Rect(actorProp.location[0],
                                     actorProp.location[1],
                                     actorProp.hitpoints,
                                     5))
    
    
    def drawAllActors(self, screen, ws):
        for _, actorProp in ws.actors:
            self.drawActor(screen, actorProp)
    
    def updateDisplay(self, msgArgs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                             and event.key == pygame.K_ESCAPE):
                
                print self.channel, "--APP_EXIT-->", self.world
                # self.world.send((self.channel, "PRINT_INFO"))
                self.world.send((self.channel, "STOP_TICK_LOOP"))
                
        screen = pygame.display.get_surface()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200, 200, 200))
        screen.blit(background, (0, 0))
        
        self.frame += 1
        
        ws = msgArgs[0]
        
        self.drawTerrainTiles(screen, ws)
        self.drawPathFindTest(screen, ws)
        self.drawAllActors(screen, ws)
        self.drawBuildingTiles(screen, ws)
        self.drawCollisionTiles(screen, ws)
        
        pygame.display.flip()
        
        # print("We have",stackless.runcount,"tasklet(s).")
