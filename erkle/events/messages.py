from erkle import *

@irc.event("notice", "erkle.events.messages")
def ntc(connection,sender,message):
	print("notice: "+sender+": "+message)

@irc.event("action", "erkle.events.messages")
def fed(connection,nickname,host,target,message):
	print(target+" "+nickname+"("+host+") "+message)

@irc.event("public", "erkle.events.messages")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+"("+host+"): "+message)

@irc.event("private", "erkle.events.messages")
def fed(connection,nickname,host,message):
	print(connection.nickname+" "+nickname+"("+host+"): "+message)
