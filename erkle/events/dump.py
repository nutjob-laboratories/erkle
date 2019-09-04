from erkle import *

"""
	display.py

"""

@hook.event('kick')
def evkick(connection,nickname,host,channel,target,message):
	if message:
		print(nickname+"("+host+") "+" kicked "+target+" from "+channel+": "+message)
	else:
		print(nickname+"("+host+") "+" kicked "+target+" from "+channel)

@hook.event('kicked')
def evkick(connection,nickname,host,channel,message):
	if message:
		print(nickname+"("+host+") "+" kicked you from "+channel+": "+message)
	else:
		print(nickname+"("+host+") "+" kicked you from "+channel)

@hook.event('mode')
def evmode(connection,nickname,host,target,mode):
	print(nickname+" set mode "+mode+" on "+target)

@hook.event('topic')
def evtopic(connection,nickname,host,channel,topic):
	if topic:
		print(nickname+"("+host+") "+" set the topic in "+channel+" to "+topic)
	else:
		print(nickname+"("+host+") "+" set the topic in "+channel+" to nothing")

@hook.event("back")
def evb(connection):
	print("You are back")

@hook.event("away")
def awy(connection,nickname,reason):
	if nickname==connection.nickname:
		print("You have been set as away")
	else:
		if reason:
			print(nickname+" is away ("+reason+")")
		else:
			print(nickname+" is away")

@hook.event("notice")
def ntc(connection,sender,message):
	print("notice: "+sender+": "+message)

@hook.event("motd")
def mt(connection,motd):
	print(motd)

@hook.event("welcome")
def con(connection):
	print("Registered with "+connection.server+":"+str(connection.port))

@hook.event("connect")
def bla(connection):
	print("Connected to "+connection.server+":"+str(connection.port))

@hook.event("nick-taken")
def glarp(connection,newnick):
	print("You nick was changed to "+newnick)

@hook.event("action")
def fed(connection,nickname,host,target,message):
	print(target+" "+nickname+"("+host+") "+message)

@hook.event("public")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+"("+host+"): "+message)

@hook.event("private")
def fed(connection,nickname,host,message):
	print(connection.nickname+" "+nickname+"("+host+"): "+message)

@hook.event("ping")
def png(connection):
	print("Ping? Pong!")

@hook.event("nick")
def ni(connection,nickname,host,newnick):
	print(nickname+"("+host+") "+" is now known as "+newnick)

@hook.event("names")
def evn(connection,channel,userlist):
	print(channel+" "+",".join(userlist))

@hook.event("quit")
def evq(connection,nickname,host,reason):
	if reason:
		print(nickname+"("+host+") "+" quit ("+reason+")")
	else:
		print(nickname+"("+host+") "+" quit")

@hook.event("part")
def evp(connection,nickname,host,channel,reason):
	if reason:
		print(nickname+"("+host+") left "+channel+" ("+reason+")")
	else:
		print(nickname+"("+host+") left "+channel)

@hook.event("join")
def evj(connection,nickname,host,channel):
	print(nickname+"("+host+") joined "+channel)
