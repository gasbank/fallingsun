import pygame
import collections

LINE_HEIGHT = 26
MAX_LINE = 4
#OFFSET_Y = 100
TEXT_COLOR = (0,50,240)
PANEL_WIDTH = 32*10
PANEL_HEIGHT = LINE_HEIGHT*MAX_LINE
MAX_AGE = 10
SCROLL_SPEED = 3

#LineInstance = collections.namedtuple('LineInstance', 'label age y yt')
class LineInstance(object): pass

class DAlertManager(object):
    @property
    def panel(self): return self._panel
    
    def __init__(self, display):
        self._display = display
        self._font = pygame.font.Font('C:\windows\Fonts\GULIM.TTC', 20)
        self._panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self._msgs = []
        
    def addText(self, msg):
        m = LineInstance()
        m.label = self._font.render(msg, 1, TEXT_COLOR)
        m.age = 0
        m.yt = PANEL_HEIGHT-32
        m.y = PANEL_HEIGHT
        
        self._msgs.append(m)
        
        for m in self._msgs[:-1]:
            m.yt -= 32
        
    def update(self, deltaTime):
        self._panel.fill((0,0,0))
        for m in self._msgs:
            m.age += deltaTime
            m.y = max(m.y - SCROLL_SPEED, m.yt)
        
        self._msgs = [m for m in self._msgs if m.age < MAX_AGE]
        
        for i, m in enumerate(reversed(self._msgs[-MAX_LINE:])):
            self._panel.blit(m.label, ((PANEL_WIDTH-m.label.get_width())/2,
                                       m.y))
