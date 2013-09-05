import pygame
import weakref

COM_PANEL_WIDTH = 32*16
COM_PANEL_HEIGHT = 32*4

class ComPanelManager(object):
    
    @property
    def panel(self):
        return self._panel
    
    @property
    def animating(self):
        return len(self._text) > 0
    
    def __init__(self):
        self._panel = pygame.Surface((COM_PANEL_WIDTH, COM_PANEL_HEIGHT))
        self.font = pygame.font.Font('C:\windows\Fonts\malgunbd.ttf', 22)
        
        self.clear()
        
    def clear(self):
        self._panel.fill((100, 100, 100))
        self._vocaTarget = None
        self._vocas = None
        self._text = []
        self._textIndex = 0
        self._lastBlitPos = [0,0]
        self._lastTextHeight = -1
        self._dialog = None
        self._dialogIndex = 0
        self._color = (255,255,255)
        
    def setVocas(self, targetName, target, vocas, dialog):
        
        if dialog is self._dialog:
            if self.animating:
                self.blitCharacter(9999)
            else:
                self.nextDialog()
            return
        
        self.clear()
        
        self._vocaTarget = weakref.ref(target)
        self._vocas = vocas
        self._dialog = dialog
        self._targetName = targetName
        
        text = ''
        text += targetName + '\n'
        
        if dialog:
            text += dialog.greetings()[self._dialogIndex] + '\n'
        
        for i, v in enumerate(vocas):
            text += '%d. %s' % (i+1,v) + '\n'
        
        self._text = list(text)
        
    def nextDialog(self):
        self._dialogIndex += 1
        if len(self._dialog.greetings()) > self._dialogIndex:
            self._panel.fill((100, 100, 100), (0,32,COM_PANEL_WIDTH,
                                               COM_PANEL_HEIGHT))
            self._textIndex = 0
            self._lastBlitPos = [0,0]
                  
            text = ''
            text += self._targetName + '\n'
            if self._dialog:
                text += self._dialog.greetings()[self._dialogIndex] + '\n'
                
            self._text = list(text)
    
    def blitCharacter(self, num=4):
        
        for _ in range(num):
            if self._text:
                ch = self._text.pop(0)
                if ch == '\n':
                    self._lastBlitPos[0] = 0
                    self._lastBlitPos[1] += self._lastTextHeight
                elif ch == '{':
                    self._color = (0,255,255)
                elif ch == '}':
                    self._color = (255,255,255)
                else:
                    if self._lastBlitPos[0] >= COM_PANEL_WIDTH-32 and len(self._text) > 1:
                        self._lastBlitPos[0] = 0
                        self._lastBlitPos[1] += self._lastTextHeight
                        
                    if self._lastBlitPos[0] == 0 and ch == ' ':
                        continue
                    
                    text = self.font.render(ch, 1, self._color)
                    self._panel.blit(text, self._lastBlitPos)
                    self._lastBlitPos[0] += text.get_width()
                    self._lastTextHeight = max(self._lastTextHeight,
                                               text.get_height())
            else:
                break
    
    def update(self, actorsDict, deltaTime):
        if self._vocaTarget and (self._vocaTarget() is None
                                 or not actorsDict.has_key(self._vocaTarget())):
            self.clear()
        
        self.blitCharacter()