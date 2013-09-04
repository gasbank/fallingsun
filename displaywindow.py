# coding: utf-8
from actor import SActor, ActorProperties
import pygame
import os
from sight import SSight

TS = 32  # Tile Size
STS = 16  # Sub-Tile Size
EAST, WEST, SOUTH, NORTH = 0,1,2,3    
            
ARROW_KEY_MAPPING = {pygame.K_RIGHT:'E',
                     pygame.K_LEFT:'W',
                     pygame.K_UP:'N',
                     pygame.K_DOWN:'S'}

KEYPAD_KEY_MAPPING = {pygame.K_KP4:WEST,
                      pygame.K_KP6:EAST,
                      pygame.K_KP8:NORTH,
                      pygame.K_KP2:SOUTH}

class FadeoutText(object):
    def __init__(self, font, text, location, maxAge=5.0, color=(0,0,0),
                 maxOffset=10.0):
        self._label = font.render(text, 1, color)
        self._age = 0
        self._maxAge = maxAge
        self._location = location
        self._maxOffset = maxOffset
    
    @property
    def ageRatio(self):
        return max(0.0, min(self._age / self._maxAge, 1.0))
        
    @property
    def location(self):
        return (self._location[0],
                self._location[1] - self.ageRatio * self._maxOffset)
        
    @property
    def dead(self):
        return self._age >= self._maxAge
        
    def draw(self, deltaTime):
        if not self.dead:
            screen = pygame.display.get_surface()
            screen.blit(self._label, self.location)
            self._age += deltaTime

        
class SDisplayWindow(SActor):
    @property
    def camOrigin(self):
        return (-self.camX,-self.camY)
    @property
    def camOriginTile(self):
        return (int(-self.camX//TS),int(-self.camY//TS))
    @property
    def camLastTile(self):
        return (int((-self.camX+self.swidth)//TS)+1,
                int((-self.camY+self.sheight)//TS)+1)

    def __init__(self, world, windowTitle='Falling Sun', client=None,
                 swidth=TS*10, sheight=TS*10, sightedActorsOnly=False):
        SActor.__init__(self, 'DisplayWindow')
        self.frame = 0
        self.world = world
        self.icons = {}
        self.time = 0
        self._client = client
        self.swidth = swidth
        self.sheight = sheight
        self.sightedActorsOnly = sightedActorsOnly
        self.sightedActors = None
        
        self.camX = self.camY = 0
        self.camdX = self.camdY = 0
        self.camKey = [False]*4
        self.camOff = None
        
        VPX = swidth//TS
        VPY = sheight//TS
        
        pygame.init()
        pygame.display.set_caption(windowTitle)
        pygame.display.set_mode((swidth+TS*2, sheight+TS*2))
        self.mainSurface = pygame.Surface((TS*VPX,TS*VPY))
        
        self._fadeoutTexts = []
        self.font = pygame.font.Font('C:\windows\Fonts\GULIM.TTC', 10)
        self.bigFont = pygame.font.Font('C:\windows\Fonts\ARIALNBI.ttf', 12)
        self.dustRoadTile = pygame.image.load(os.path.join('data', '004-G_Ground02.png'))
        self.waterTile = pygame.image.load(os.path.join('data', '001-G_Water01.png'))
        self.grasslandTile = pygame.image.load(os.path.join('data', '001-Grassland01.png'))
        self.fighterTile = pygame.image.load(os.path.join('data', '001-Fighter01.png'))
        self.thiefTile = pygame.image.load(os.path.join('data', '018-Thief03.png'))
        self.farmerTile = pygame.image.load(os.path.join('data', '143-Farmer01.png'))
        self.headmanTile = pygame.image.load(os.path.join('data', '109-Civilian09.png'))
        
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         public=False,
                                         instanceName=self.instanceName)))
        self.world.send((self.channel, "TELL_ME_WORLD_SIZE"))
        
        if client:
            client.send((self.channel, 'I_AM_DISPLAY'))
        
        self.debug('Created.')
        
    def defaultMessageAction(self, args):
        _, msg, msgArgs = args[0], args[1], args[2:]
        if msg == 'WORLD_STATE':
            self.updateDisplay(msgArgs)
        elif msg == 'DRAW_FADEOUT_TEXT':
            self._fadeoutTexts.append(FadeoutText(self.bigFont, msgArgs[0],
                                                  msgArgs[1]))
        elif msg == 'WORLD_SIZE':
            icon = pygame.image.load(os.path.join('data', 'fighter.ico')).convert_alpha()
            pygame.display.set_icon(icon)
        
        elif msg == 'SIGHTED_ACTORS':
            if self.sightedActorsOnly:
                self.sightedActors = msgArgs[0]
        else:
            raise RuntimeError('Unknown message: %s' % msg)
        
    def getIcon(self, iconName):
        if self.icons.has_key(iconName):
            return self.icons[iconName]
        else:
            iconFile = os.path.join("data", "%s.bmp" % iconName)
            surface = pygame.image.load(iconFile)
            surface.set_colorkey((0xf3, 0x0a, 0x0a))
            self.icons[iconName] = surface
            return surface
    

    def drawAutotiles(self, screen, ws, tile, i, j, anim, c):
        
        neighbors = ws.tileData.getNeighborSameString(j, i, c)
        
        animFrame = (self.frame / 80) % 4 if anim else 0
        
        #self.blitTile(screen, self.waterTile, (tx,ty), camOff, area)
        
        blitCalls = []
        
        if neighbors == '0000':
            area = (TS * 0, TS * 0, TS, TS)
            blitCalls.append((  (TS * j, TS * i), area))
            
        # <--->
        elif neighbors == '1000':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS, STS * 2)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS, STS * 2)))
        elif neighbors == '0100':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS, STS * 2)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS, STS * 2)))
        elif neighbors == '1100':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS, STS * 2)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS, STS * 2)))
            
        # A
        # |
        # |
        # |
        # V
        elif neighbors == '0010':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 2, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 2, STS)))
        elif neighbors == '0001':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 2, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 2, STS)))
        elif neighbors == '0011':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 2, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 2, STS)))
        
        # <---+
        #     |
        #     V
        elif neighbors == '0110':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS))) # ##
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 1 + STS * 1, STS * 1, STS)))

        # +--->
        # |
        # V
        elif neighbors == '0101':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 1 + STS * 1, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS)))  # ##
            
        # A
        # |
        # +--->
        elif neighbors == '1001':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 3 + STS * 1, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 1, TS * 3 + STS * 1, STS * 1, STS)))
            
        #     A
        #     |
        # <---+
        elif neighbors == '1010':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 3 + STS * 1, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 3 + STS * 1, STS * 1, STS)))
            
        
        #     A
        #     |
        # <---+
        #     |
        #     V
        elif neighbors == '1110':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 2 + STS * 1, STS * 1, STS)))    
            
        # A
        # |
        # +--->
        # |
        # V
        elif neighbors == '1101':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 0 + STS * 0, TS * 2 + STS * 1, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS)))  # ##
        
        #    A
        #    |
        # <--+-->
        elif neighbors == '1011':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 0, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 3 + STS * 1, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 3 + STS * 1, STS * 1, STS)))
            
        # <--+-->
        #    |
        #    V
        elif neighbors == '0111':
            blitCalls.append(((TS * j    , TS * i), (3 * TS * animFrame + TS * 1 + STS * 0, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j + STS, TS * i), (3 * TS * animFrame + TS * 1 + STS * 1, TS * 1 + STS * 0, STS * 1, STS)))
            blitCalls.append(((TS * j    , TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 0, TS * 0 + STS * 1, STS * 1, STS)))  # ##
            blitCalls.append(((TS * j + STS, TS * i + STS), (3 * TS * animFrame + TS * 2 + STS * 1, TS * 0 + STS * 1, STS * 1, STS)))  # ##
            
        #      A
        #      |
        #  <---+--->
        #      |
        #      V
        elif neighbors == '1111':
            area = (TS * 2, TS * 0, TS, TS)
            blitCalls.append(((TS * j, TS * i), area))
        else:
            area = (TS * 1, TS * 2, TS, TS)
            blitCalls.append(((TS * j, TS * i), area))
        
        # blit call
        for bc in blitCalls:
            self.blitTilePixelSpace(screen, tile, *bc)

    def getTileBlitLoc(self, tIndex):
        tx, ty = tIndex
        return (self.camOff[0] + TS * (tx-self.camOriginTile[0]),
                self.camOff[1] + TS * (ty-self.camOriginTile[1]))    
        
    def getTileBlitLocFromPixelSpace(self, destPixel):
        destX, destY = destPixel
        return (self.camOff[0] + destX - TS*self.camOriginTile[0],
                self.camOff[1] + destY - TS*self.camOriginTile[1])
    
    def blitTile(self, screen, tile, tIndex, area):
        screen.blit(tile, self.getTileBlitLoc(tIndex), area)
    
    def blitTilePixelSpace(self, screen, tile, destPixel, area):
        screen.blit(tile, self.getTileBlitLocFromPixelSpace(destPixel), area)
    
    def drawTerrainTiles(self, screen, ws):
        
        for ty in range(self.camOriginTile[1], self.camLastTile[1]):
            for tx in range(self.camOriginTile[0], self.camLastTile[0]):
                
                t, _, _ = ws.tileData.getCellData(tx, ty)
                
                autoTile = None
                autoTileAnim = False
                
                if t == 0:
                    area = (TS * 1, TS * 0, TS, TS)
                    self.blitTile(screen, self.waterTile, (tx,ty), area)
                elif t == 1:
                    autoTile = self.waterTile
                    autoTileAnim = True
                elif t == 2:
                    autoTile = self.dustRoadTile
                else:
                    raise RuntimeError('wtf')
                
                if autoTile:
                    self.drawAutotiles(screen, ws, autoTile, ty, tx,
                                       autoTileAnim, t)
                    
    def drawBuildingTiles(self, screen, ws, ground):
        
        for ty in range(self.camOriginTile[1], self.camLastTile[1]):
            for tx in range(self.camOriginTile[0], self.camLastTile[0]):
                
                _, b, _ = ws.tileData.getCellData(tx, ty)
                
                if b == 2:
                    # Tent sprite
                    spriteX = 0
                    spriteY = 13
                    spriteWidth = 5
                    spriteHeight = 5
                    drawOffsetX = 0
                    drawOffsetY = 0
                    sampleOffsetX = 0
                    sampleOffsetY = 0
                    
                elif b == 3:
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
                        
                        if ws.tileData.collision[ty+ii][tx+jj] == ground:
                            
                            self.blitTilePixelSpace(screen, self.grasslandTile,
                                                    (TS * tx + drawOffsetX + TS*jj,
                                                     TS * ty + drawOffsetY + TS*ii), 
                                                    (TS * spriteX + STS * 0 + TS*jj + sampleOffsetX, 
                                                     TS * spriteY + STS * 0 + TS*ii + sampleOffsetY, 
                                                     TS, TS))
        
    def drawGroundBuildingTiles(self, screen, ws):
        
        self.drawBuildingTiles(screen, ws, 1)

    
    def drawUpperBuildingTiles(self, screen, ws):
        
        self.drawBuildingTiles(screen, ws, 0)
                    
    
    def drawCollisionTiles(self, screen, ws):
        
        for ty in range(self.camOriginTile[1], self.camLastTile[1]):
            for tx in range(self.camOriginTile[0], self.camLastTile[0]):
                
                locX, locY = self.getTileBlitLoc((tx,ty))
                
                if not ws.tileData.isMovable(tx, ty):
                    pygame.draw.rect(screen, (255, 128, 0),
                                     pygame.Rect(locX, locY, TS, TS), 1)
        
    def drawPathFindTest(self, screen, ws):
        
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
        
        
    def drawAnimatedCharacterSprite(self, screen, actorProp, tileType):
        
        i = actorProp.location[0] / TS
        j = actorProp.location[1] / TS
        
        drawXOffset = -STS
        drawYOffset = -TS-STS//2
        
        animFrame = (actorProp.velocity * self.frame / 200) % 4
        direction = self.getDirectionFromAngle(actorProp.angle)
        
        self.blitTilePixelSpace(screen, tileType,
                                (TS * i + drawXOffset, TS * j + drawYOffset), 
                                (1 * TS * animFrame + TS * 0 + STS * 0,
                                 (TS * 1 + STS * 1) * direction,
                                 TS * 1, TS * 1 + STS))
        
    def drawActor(self, screen, actorProp):
        
        actorImageMap = {'SPrey': self.fighterTile,
                         'SWoodcutter': self.farmerTile,
                         'SHeadman': self.headmanTile}
        
        if actorProp.animatedSprite:
            
            if actorProp.name in ['SPrey', 'SWoodcutter']:
                itemImage = actorImageMap[actorProp.name]
            elif actorProp.name == 'SBlank':
                if actorImageMap.has_key(actorProp.blankType):
                    itemImage = actorImageMap[actorProp.blankType]
                else:
                    return 
            else:
                raise RuntimeError('Not available for the moment.')
            
            self.drawAnimatedCharacterSprite(screen, actorProp, itemImage)
        
        elif actorProp.staticSprite:
            
            pass
        
        else:
        
            itemImage = self.getIcon(actorProp.name)
            itemImage = pygame.transform.rotate(itemImage, -actorProp.angle)
            screen.blit(itemImage, actorProp.location)
        
        
        nameplateLoc = list(self.getTileBlitLocFromPixelSpace(actorProp.location)) #list(actorProp.location)
        
        hitpointsDrawHeight = 5
        waitGaugeDrawHeight = 5
        
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
        
        if actorProp.intention:
            label = self.font.render(actorProp.intention, 1, (0, 0, 0))
            pygame.draw.rect(screen, bgColor, (nameplateLoc[0],
                                               nameplateLoc[1],
                                               label.get_width(),
                                               label.get_height()))
            screen.blit(label, nameplateLoc)
            nameplateLoc[1] += label.get_height()
    
        # The wait gauge
        if actorProp.waitGauge > 0:
            
            pygame.draw.rect(screen, (0, 0, 255),
                             pygame.Rect(nameplateLoc[0],
                                         nameplateLoc[1],
                                         actorProp.waitGauge,
                                         waitGaugeDrawHeight))
            nameplateLoc[1] += waitGaugeDrawHeight
    

    def drawSightDebug(self, screen, actorProp):
        
        loc = [loc - TS*actorProp.sightRange for loc in actorProp.location]
        loc = self.getTileBlitLocFromPixelSpace(loc) 
        
        pygame.draw.rect(screen, (255, 255, 255),
                         pygame.Rect(loc[0], loc[1],
                                     32*(actorProp.sightRange*2+1),
                                     32*(actorProp.sightRange*2+1)),
                         1)
    
    
    def drawListedActors(self, screen, actors):
        
        for _, p in actors:
            if p.physical:
                self.drawActor(screen, p)
            elif p.name == 'SSight':
                self.drawSightDebug(screen, p)
    
    
    def drawFadeoutTexts(self, screen):
        for ft in self._fadeoutTexts:
            ft.draw(self.deltaTime)
    
        self._fadeoutTexts = [ft for ft in self._fadeoutTexts if not ft.dead]
    

    def drawGridDebug(self, screen):
        
        for tx in range(self.camOriginTile[0], self.camLastTile[0]):
            pygame.draw.line(screen, (128,128,128), self.getTileBlitLoc((tx, self.camOriginTile[1])), self.getTileBlitLoc((tx, self.camLastTile[1])))
            
        for ty in range(self.camOriginTile[1], self.camLastTile[1]):
            pygame.draw.line(screen, (128,128,128), self.getTileBlitLoc((self.camOriginTile[0], ty)), self.getTileBlitLoc((self.camLastTile[0], ty)))
            
        for ty in range(self.camOriginTile[1], self.camLastTile[1]):
            for tx in range(self.camOriginTile[0], self.camLastTile[0]):
                label = self.font.render('%d,%d'%(tx,ty), 1, (0, 0, 0))
                screen.blit(label, self.getTileBlitLoc((tx, ty)))
    
    def handleMoveKeyEvent(self, event):
        if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            
            pressed = event.type == pygame.KEYDOWN
            
            arrowAction = ARROW_KEY_MAPPING.get(event.key, None)
            if arrowAction is not None:
                self._client.send((self.channel, 'MOVE_PAWN', arrowAction,
                                   pressed))
            
            kpAction = KEYPAD_KEY_MAPPING.get(event.key, None)
            if kpAction is not None:
                self.camKey[kpAction] = pressed

            if event.key == pygame.K_KP5:
                self.camX = self.camY = 0
                
    
    def drawActors(self, screen, ws):
        
        actors = [] # Actors to draw...
        
        if self.sightedActorsOnly:
            if self.sightedActors:
                actors += [(aRef(),ws.actorsDict[aRef()])
                           for _, _, aRef in self.sightedActors if aRef()]
            
            if ws.actorsDict[self._client].name == 'SSight':
                actors.append((self._client, ws.actorsDict[self._client]))
                
        else:
            actors = ws.actors # All actors!

        # Y-sort
        actors = sorted(actors, key=lambda a: a[1].location[1])
        
        # Draw!
        self.drawListedActors(screen, actors)
    
    def updateDisplay(self, msgArgs):
        ws = msgArgs[0]
        self.deltaTime = ws.time - self.time
        self.time = ws.time
        
        for event in pygame.event.get():
            if any((event.type == pygame.QUIT,
                    (event.type == pygame.KEYDOWN
                     and event.key == pygame.K_ESCAPE))):
                
                self.info('--%s--> %s' % ('CLOSE_WINDOW', self.world))
                self.world.send((self.channel, "CLOSE_WINDOW"))
            
            if self._client:
                self.handleMoveKeyEvent(event)
                
        screen = pygame.display.get_surface()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200, 200, 200))
        screen.blit(background, (0, 0))
        
        self.frame += 1
        
        SCROLL_SPEED = TS
        self.camX += SCROLL_SPEED * (self.camKey[EAST] - self.camKey[WEST])
        self.camY += SCROLL_SPEED * (self.camKey[SOUTH] - self.camKey[NORTH])
        
        tileO = tuple((v*TS for v in self.camOriginTile))
        self.camOff = tuple((tileO[i] - self.camOrigin[i] for i in range(2)))
        
        
        screen = self.mainSurface
        
        self.drawTerrainTiles(screen, ws)
        self.drawGridDebug(screen)
        self.drawCollisionTiles(screen, ws)
        #self.drawPathFindTest(screen, ws)
        self.drawGroundBuildingTiles(screen, ws)
        self.drawActors(screen, ws)
        self.drawUpperBuildingTiles(screen, ws)
        self.drawFadeoutTexts(screen)
        
        screen = pygame.display.get_surface()
        screen.blit(self.mainSurface, (TS,TS))
        
        label = self.font.render('TL Origin %s' % str(self.camOrigin),
                                 1, (0, 0, 0))
        screen.blit(label, (0, 0))
        
        pygame.display.flip()
        
        # print("We have",stackless.runcount,"tasklet(s).")
