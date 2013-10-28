import stackless

def Sending(channel):
    print "sending"
    channel.send("foo")

def DummyMe():
    while 1:
        pass
    

ch = stackless.channel()

task = stackless.tasklet(Sending)(ch)
#task2 = stackless.tasklet(DummyMe)()

stackless.run()

print "Channel balance is ", ch.balance
print ch.receive()