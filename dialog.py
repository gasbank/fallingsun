# coding:utf-8
import weakref
import stackless

class Context(object):
    @property
    def target(self): return self._target
    @property
    def starter(self): return self._starter
    @property
    def conversation(self): return self._conversation
    
    def __init__(self, conversation, starter, target):
        assert isinstance(conversation, Conversation)
        assert isinstance(starter, stackless.channel)
        assert isinstance(target, stackless.channel)
        
        self._conversation = conversation
        self._starter = weakref.ref(starter)
        self._target = weakref.ref(target)

class Choice(object):
    @property
    def text(self): return self._text
    
    def __init__(self, text):
        self._text = text
        
class StartTutorialChoice(Choice):
    pass

class Conversation(object): pass

class HeadmanAssistant(Conversation):
    @property
    def greetings(self):
        return (u'어서오세요. 이번에 새로 막촌의 장으로 부임하신 분이시군요.',
                u'만나서 반갑습니다. 저는 막촌의 신임 촌장의 보좌를 담당하는 {스미스}라고 합니다.',
                u'본격적인 촌장직의 업무 안내에 앞서 우선 기본적인 업무를 수행하실 수 있는지 확인해야 합니다.',
                u'뭐, 통상적인 절차니까요. 지금 잠깐 시간 괜찮으신지요?',
                (StartTutorialChoice(u'네.'), StartTutorialChoice(u'아뇨.')))
    
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
    
