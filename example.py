
from erkle import *

import sys

@hook.event("back")
def evb(connection):
	print("you are back")

@hook.event("away")
def awy(connection,nickname,reason):
	if nickname==connection.nickname:
		print("you have been set as away")
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
	connection.send("JOIN #quirc")

@hook.event("connect")
def bla(connection):
	print("connected")

@hook.event("nick-taken")
def glarp(connection,newnick):
	print("nick changed to "+newnick)

@hook.event("action")
def fed(connection,nickname,host,target,message):
	print(nickname+" "+message)

@hook.event("public")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+" "+message)
	if message.lower()=="quit":
		sys.exit()

@hook.event("private")
def fed(connection,nickname,host,message):
	print("private "+nickname+" "+message)

@hook.event("ping")
def png(connection):
	print("ping")

@hook.event("nick")
def ni(connection,nickname,host,newnick):
	print(nickname+" is now known as "+newnick)

@hook.event("names")
def evn(connection,channel,userlist):
	print(userlist)

@hook.event("quit")
def evq(connection,nickname,host,reason):
	print(nickname+" quit")

@hook.event("part")
def evp(connection,nickname,host,channel,reason):
	print(nickname+" left "+channel)

@hook.event("join")
def evj(connection,nickname,host,channel):
	print(nickname+" joined "+channel)

c = ErkleClient("mybot","mybotu","my bot","localhost",6667,None,False)
c.connect()

