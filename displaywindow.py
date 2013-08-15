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
        
        self.font = pygame.font.SysFont("monospace", 15)
        
        pygame.display.set_mode((swidth, sheight))
        pygame.display.set_caption("MmoActor")
        #print self.channel, "--JOIN-->", self.world
        self.world.send((self.channel, "JOIN",
                         ActorProperties(self.__class__.__name__,
                                         public=False)))
        #print("DisplayWindow created")
    
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
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                print self.channel, "--APP_EXIT-->", self.world
                self.world.send((self.channel, "PRINT_INFO"))
                
        screen = pygame.display.get_surface()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200,200,200))
        screen.blit(background, (0, 0))
        
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
