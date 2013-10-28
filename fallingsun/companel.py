import pygame
import weakref
import os
import dialog

COM_PANEL_WIDTH = 32*(3+16) # Three for a speaker's face blitting area
COM_PANEL_HEIGHT = 32*(3+1)
DIALOG_BLIT_X0 = 32*3 + 16
DIALOG_BLIT_Y0 = 0
TEXT_RIGHT_MARGIN = 32
SPEAKER_HEIGHT = 32
PANEL_BGCOLOR = (100,100,100)
DEFAULT_TEXT_COLOR = (255,255,255)
NAME_TEXT_COLOR = (0,255,255)

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
        
        self._faceTile = pygame.image.load(os.path.join('../data', 'Evil.png'))
        
        self.clear()
        
    def clear(self):
        self._panel.fill(PANEL_BGCOLOR)
        
        # Drawing context
        self._text = []
        self._textIndex = 0
        self._lastBlitPos = [DIALOG_BLIT_X0,DIALOG_BLIT_Y0]
        self._lastTextHeight = -1
        self._color = DEFAULT_TEXT_COLOR
        
        # Dialog context
        self._dialogContext = None
        '''
        self._vocaTarget = None
        self._vocas = None        
        self._conversation = None
        '''
        
    def setDialogContext(self, context):
        
        # Proceed to the next line if the same conversation is set again.
        if context is self._dialogContext:
            # Previous lines still printing...
            if self.animating:
                # Print out all characters at once.
                self.blitCharacter(len(self._text))
            else:
                # Proceed to next dialog.
                self.nextDialog()
            return
        
        # A new conversation begins.
        self.clear()
        
        self._dialogContext = context
        
        self._dialogContext.proceed()
        
        #self._vocaTarget = weakref.ref(target) if target else None
        #self._vocas = vocas
        #self._conversation = conversation
        #self._targetName = conversation.speaker
        
        text = ''
        text += self._dialogContext.speaker + '\n'
        text += self._dialogContext.line + '\n'
        
        '''
        for i, v in enumerate(vocas):
            text += '%d. %s' % (i+1,v) + '\n'
        '''
        
        self._text = list(text)
        
        # Blit the speaker's face.
        self._panel.blit(self._faceTile, (0,0),
                         self.getFaceTileRect(self._dialogContext.faceTile))
        
    def getFaceTileRect(self, faceTile):
        return (32*3*faceTile[0], 32*3*faceTile[1], 32*3, 32*3)
    
    def clearDialog(self):
        self._panel.fill(PANEL_BGCOLOR, (DIALOG_BLIT_X0,
                                         SPEAKER_HEIGHT,
                                         COM_PANEL_WIDTH,
                                         COM_PANEL_HEIGHT))
        self._textIndex = 0
        self._lastBlitPos = [DIALOG_BLIT_X0,DIALOG_BLIT_Y0]
        
    def nextDialog(self):
        
        if self._dialogContext.proceed():
            
            if self._dialogContext.isChoice:
                
                choices = self._dialogContext.line
                
                # Print choices
                self._text += ' '.join(['%d. %s' % (i+1, c.text)
                                        for i, c in enumerate(choices)])
            else:
                # Print next dialogue
                self.clearDialog()
                      
                text = ''
                text += self._dialogContext.speaker + '\n'
                text += self._dialogContext.line + '\n'
                    
                self._text = list(text)
    
    def blitCharacter(self, num=4):
        '''
        Blit characters stored by popping a character from 'self._text'
        'num' times. Do some line spliitings and text colorings also.
        '''

        for _ in range(num):
            if self._text:
                ch = self._text.pop(0)
                if ch == '\n':
                    self._lastBlitPos[0] = DIALOG_BLIT_X0
                    self._lastBlitPos[1] += self._lastTextHeight
                elif ch == '{':
                    self._color = NAME_TEXT_COLOR
                elif ch == '}':
                    self._color = DEFAULT_TEXT_COLOR
                else:
                    if self._lastBlitPos[0] >= COM_PANEL_WIDTH-TEXT_RIGHT_MARGIN and len(self._text) > 1:
                        self._lastBlitPos[0] = DIALOG_BLIT_X0
                        self._lastBlitPos[1] += self._lastTextHeight
                        
                    if self._lastBlitPos[0] == DIALOG_BLIT_X0 and ch == ' ':
                        continue
                    
                    text = self.font.render(ch, 1, self._color)
                    self._panel.blit(text, self._lastBlitPos)
                    self._lastBlitPos[0] += text.get_width()
                    self._lastTextHeight = max(self._lastTextHeight,
                                               text.get_height())
            else:
                break
    
    def update(self, actorsDict, deltaTime):
        '''
        if self._vocaTarget and (self._vocaTarget() is None
                                 or not actorsDict.has_key(self._vocaTarget())):
            self.clear()
        '''
        
        self.blitCharacter()