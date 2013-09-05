import pygame
import weakref

COM_PANEL_WIDTH = 32*16
COM_PANEL_HEIGHT = 32*4

class ComPanelManager(object):
    
    @property
    def panel(self):
        return self._panel
    
    def __init__(self):
        self._panel = pygame.Surface((COM_PANEL_WIDTH, COM_PANEL_HEIGHT))
        self.clear()
        
        self._vocaTarget = None
        self._vocas = None
        
        self.font = pygame.font.Font('C:\windows\Fonts\ARIALNBI.ttf', 20)
        
    def clear(self):
        self._panel.fill((100, 100, 100))
        self._vocaTarget = None
        self._vocas = None
        
    def setVocas(self, targetName, target, vocas):
        
        self.clear()
        
        self._vocaTarget = weakref.ref(target)
        self._vocas = vocas
        
        pos = [0,0]
        
        text = self.font.render(targetName, 1, (255,255,255))
        self._panel.blit(text, pos)
        pos[1] += text.get_height()
        
        for i, v in enumerate(vocas):
            text = self.font.render('%d. %s' % (i+1,v), 1, (255,255,255))
            self._panel.blit(text, pos)
            pos[1] += text.get_height()
    
    def update(self, deltaTime):
        if self._vocaTarget and self._vocaTarget() is None:
            self.clear()
