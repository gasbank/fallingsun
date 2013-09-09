import pygame

LINE_HEIGHT = 26
MAX_LINE = 4
#OFFSET_Y = 100
TEXT_COLOR = (0,50,240)
PANEL_WIDTH = 32*10
PANEL_HEIGHT = LINE_HEIGHT*MAX_LINE
MAX_AGE = 10
SCROLL_SPEED = 3


class DAlertManager(object):
    @property
    def panel(self): return self._panel
    
    def __init__(self, display):
        self._display = display
        self._font = pygame.font.Font('C:\windows\Fonts\GULIM.TTC', 20)
        self._panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self._msgs = []
        
    def addText(self, msg):
        self._msgs.append([self._font.render(msg, 1, TEXT_COLOR), 0, PANEL_HEIGHT-32, PANEL_HEIGHT-32])
        
        for m in self._msgs[:-1]:
            m[3] -= 32
        
    def update(self, deltaTime):
        self._panel.fill((0,0,0))
        for m in self._msgs:
            m[1] += deltaTime
            m[2] = max(m[2]-SCROLL_SPEED, m[3])
        
        self._msgs = [m for m in self._msgs if m[1] < MAX_AGE]
        
        for i, (label,_,y,yt) in enumerate(reversed(self._msgs[-MAX_LINE:])):
            self._panel.blit(label, ((PANEL_WIDTH-label.get_width())/2, y))
