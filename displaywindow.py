# coding: utf-8
from actor import SActor, ActorProperties
import pygame
import os
import logging
import math

swidth = 700
sheight = 700

class SDisplayWindow(SActor):
    def __init__(self, world):
        SActor.__init__(self)
        self.frame = 0
        self.world = world
        self.icons = {}
        pygame.init()
        
        #self.font = pygame.font.SysFont("Gulimew", 20)
        self.font = pygame.font.Font('C:\windows\Fonts\GULIM.TTC', 10)
        
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
    

    def drawAutotiles(self, screen, ws, tile, i, j, neighbors, anim=False):
        TS = 32  # Tile Size
        STS = 16  # Sub-Tile Size
        
        animFrame = (self.frame / 80) % 4 if anim else 0
        
        if neighbors == '0000':
            area = (TS * 0, TS * 0, TS, TS)
            screen.blit(tile, (TS * j, TS * i), area)
            
        # <--->
        elif neighbors == '1000':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS, STS * 2))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS, STS * 2))
        elif neighbors == '0100':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS, STS * 2))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS, STS * 2))
        elif neighbors == '1100':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS, STS * 2))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS, STS * 2))
            
        # A
        # |
        # |
        # |
        # V
        elif neighbors == '0010':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
        elif neighbors == '0001':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
        elif neighbors == '0011':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 2, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 2, STS))
        
        # <---+
        #     |
        #     V
        elif neighbors == '0110':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 1, STS * 1, STS))

        # +--->
        # |
        # V
        elif neighbors == '0101':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 1, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
            
        # A
        # |
        # +--->
        elif neighbors == '1001':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
            
        #     A
        #     |
        # <---+
        elif neighbors == '1010':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
            
        
        #     A
        #     |
        # <---+
        #     |
        #     V
        elif neighbors == '1110':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 1, STS * 1, STS))    
            
        # A
        # |
        # +--->
        # |
        # V
        elif neighbors == '1101':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 1, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
        
        #    A
        #    |
        # <--+-->
        elif neighbors == '1011':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 3 + STS * 1, STS * 1, STS))
            
        # <--+-->
        #    |
        #    V
        elif neighbors == '0111':
            screen.blit(tile, (TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j + STS, TS * i), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 1 + STS * 0, STS * 1, STS))
            screen.blit(tile, (TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))  # ##
            screen.blit(tile, (TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS))  # ##
            
        #      A
        #      |
        #  <---+--->
        #      |
        #      V
        elif neighbors == '1111':
            area = (TS * 2, TS * 0, TS, TS)
            screen.blit(tile, (TS * j, TS * i), area)
        else:
            area = (TS * 1, TS * 2, TS, TS)
            screen.blit(tile, (TS * j, TS * i), area)
    
    
    def drawTerrainTiles(self, screen, ws):
        
        TS = 32  # Tile Size
        
        for i, r in enumerate(ws.tileData.terrain):
            for j, c in enumerate(r):
                
                autoTile = None
                autoTileAnim = False
                
                if c == 0:
                    area = (TS * 1, TS * 0, TS, TS)
                    screen.blit(self.waterTile, (TS * j, TS * i), area)
                elif c == 1:
                    autoTile = self.waterTile
                    autoTileAnim = True
                elif c == 2:
                    autoTile = self.dustRoadTile
                
                if autoTile:
                    neighbors = '%d%d%d%d' % (1 if ws.tileData.terrain[i - 1][j] == c else 0,
                                              1 if ws.tileData.terrain[i + 1][j] == c else 0,
                                              1 if r[j - 1] == c else 0,
                                              1 if r[j + 1] == c else 0)
                    
                    self.drawAutotiles(screen, ws, autoTile, i, j,
                                       neighbors, autoTileAnim)
                    
    def drawBuildingTiles(self, screen, ws, ground):
        
        TS = 32  # Tile Size
        STS = 16  # Sub-Tile Size
        
        for i, r in enumerate(ws.tileData.building):
            for j, c in enumerate(r):
                
                if c == 2:
                    # Tent sprite
                    spriteX = 0
                    spriteY = 13
                    spriteWidth = 5
                    spriteHeight = 5
                    drawOffsetX = 0
                    drawOffsetY = 0
                    sampleOffsetX = 0
                    sampleOffsetY = 0
                    
                elif c == 3:
                    # Tree sprite
                    spriteX = 0
                    spriteY = 5
                    spriteWidth = 4
                    spriteHeight = 5
                    drawOffsetX = 0
                    drawOffsetY = 0
                    sampleOffsetX = 0
                    sampleOffsetY = 0
                else:
                    continue
                    
                for ii in range(spriteHeight):
                    for jj in range(spriteWidth):
                        
                        if ws.tileData.collision[i+ii][j+jj] == ground:
                
                            screen.blit(self.grasslandTile,
                                        (TS * j + drawOffsetX + TS*jj,
                                         TS * i + drawOffsetY + TS*ii), 
                                        (TS * spriteX + STS * 0 + TS*jj + sampleOffsetX, 
                                         TS * spriteY + STS * 0 + TS*ii + sampleOffsetY, 
                                         TS, 
                                         TS))
        
    def drawGroundBuildingTiles(self, screen, ws):
        
        self.drawBuildingTiles(screen, ws, 1)

    
    def drawUpperBuildingTiles(self, screen, ws):
        
        self.drawBuildingTiles(screen, ws, 0)
                    
    
    def drawCollisionTiles(self, screen, ws):
        
        TS = 32  # Tile Size

        for i, r in enumerate(ws.tileData.collision):
            for j, c in enumerate(r):
                if not ws.tileData.isMovable(j, i):
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
        
        drawXOffset = -STS
        drawYOffset = -TS-STS//2
        
        animFrame = (actorProp.velocity * self.frame / 200) % 4
        direction = self.getDirectionFromAngle(actorProp.angle)
        
        screen.blit(self.fighterTile,
                    (TS * i + drawXOffset,
                     TS * j + drawYOffset), 
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
        
        nameplateLoc = list(actorProp.location)
        
        hitpointsDrawHeight = 5
        
        # The hitpoints gauge
        pygame.draw.rect(screen, (0, 255, 0),
                         pygame.Rect(nameplateLoc[0],
                                     nameplateLoc[1],
                                     actorProp.hitpoints,
                                     hitpointsDrawHeight))
        nameplateLoc[1] += hitpointsDrawHeight
                    
        # Draw the instance name of the actor
        bgColor = (240,240,240)
        label = self.font.render(actorProp.instanceName, 1, (255, 0, 0))
        pygame.draw.rect(screen, bgColor, (nameplateLoc[0],
                                           nameplateLoc[1],
                                           label.get_width(),
                                           label.get_height()))
        screen.blit(label, nameplateLoc)
        nameplateLoc[1] += label.get_height()
        
        label = self.font.render(actorProp.intention, 1, (0, 0, 0))
        pygame.draw.rect(screen, bgColor, (nameplateLoc[0],
                                           nameplateLoc[1],
                                           label.get_width(),
                                           label.get_height()))
        screen.blit(label, nameplateLoc)
    
    
    def drawAllActors(self, screen, ws):
        
        for _, actorProp in sorted(ws.actors, key=lambda x: x[1].location[1]):
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
        self.drawCollisionTiles(screen, ws)
        #self.drawPathFindTest(screen, ws)
        self.drawGroundBuildingTiles(screen, ws)
        self.drawAllActors(screen, ws)
        self.drawUpperBuildingTiles(screen, ws)
        
        
        pygame.display.flip()
        
        # print("We have",stackless.runcount,"tasklet(s).")
