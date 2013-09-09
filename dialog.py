# coding:utf-8
import weakref
import stackless
import treasurebox

class Context(object):
    @property
    def target(self): return self._target
    @property
    def starter(self): return self._starter
    @property
    def conversation(self): return self._conversation
    @property
    def speaker(self): return self._conversation.speaker
    @property
    def line(self): return self._conversation.greetings[self._conIndex]
    @property
    def faceTile(self): return self._conversation.faceTile
    @property
    def isChoice(self):
        d = self._conversation.greetings[self._conIndex]
        if isinstance(d, tuple):
            assert all([isinstance(t, Choice) for t in d])
            return True
        return False
    @property
    def canProceed(self): return self._conIndex < len(self._conversation.greetings) - 1
    @property
    def endOfConversation(self): return self._conIndex >= len(self._conversation.greetings) - 1
    
    def __init__(self, conversation, starter, target, world):
        assert isinstance(conversation, Conversation)
        assert isinstance(starter, stackless.channel)
        assert isinstance(target, stackless.channel)
        
        self._conversation = None
        self._conIndex = -1 # Conversation Index
        
        self._starter = weakref.ref(starter)
        self._target = weakref.ref(target)
        self.world = world
        
        self._changeConversation(conversation)

    def proceed(self):
        if self.canProceed:
            self._conIndex += 1
            return True
        return False
    
    def choose(self, c):
        assert self.isChoice
        try:
            choices = self._conversation.greetings[self._conIndex]
            self._changeConversation(choices[c].conversation)
        except IndexError:
            return False
        
        return True
    
    def _changeConversation(self, c):
        assert self._conversation is not c
        self._conversation = c
        self._conIndex = -1
        self._conversation.context = self

class Conversation(object):
    @property
    def context(self): return self._context
    @context.setter
    def context(self, v):
        self._context = weakref.ref(v)
        
    def __init__(self):
        self._context = None
    

class Choice(Conversation):
    @property
    def text(self): return self._text
    
    def __init__(self, text):
        self._text = text
        
class StartTutorialChoice(Choice):
    
    @property
    def conversation(self): return self
    
    @property
    def greetings(self):
        treasurebox.STreasureBox(self._context().world, (32*22+16,32*5+16), 'TB')
        return (u'좋습니다. {보물상자}를 집어서 저에게 가져와 보십시오.',)

    @property
    def speaker(self):
        return u'스미스'
    
    @property
    def faceTile(self):
        return (0, 1)
    
class RefuseChoice(Choice):
    
    @property
    def conversation(self): return self
    
    @property
    def greetings(self):
        return (u'서둘러서 좋을 것은 없으니 시간이 되면 다시 오시지요.',)
    
    @property
    def speaker(self):
        return u'스미스'
    
    @property
    def faceTile(self):
        return (0, 1)
    

class HeadmanAssistant(Conversation):
    @property
    def greetings(self):
        return (u'어서오세요. 이번에 새로 막촌의 장으로 부임하신 분이시군요.',
                u'만나서 반갑습니다. 저는 막촌의 신임 촌장의 보좌를 담당하는 {스미스}라고 합니다.',
                u'본격적인 촌장직의 업무 안내에 앞서 우선 기본적인 업무를 수행하실 수 있는지 확인해야 합니다.',
                u'뭐, 통상적인 절차니까요. 지금 잠깐 시간 괜찮으신지요?',
                (StartTutorialChoice(u'네.'), RefuseChoice(u'아뇨.')))
    
    @property
    def speaker(self):
        return u'스미스'
    
    @property
    def faceTile(self):
        return (0, 1)
    
class Villager(Conversation):
    @property
    def greetings(self):
        return (u'무슨 일이시죠?',)
    
    @property
    def speaker(self):
        return u'케빈'
    
    @property
    def faceTile(self):
        return (0, 0)
    
