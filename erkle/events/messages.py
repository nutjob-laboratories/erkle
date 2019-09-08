from erkle import *

@irc.event("notice")
def ntc(connection,sender,message):
	print("notice: "+sender+": "+message)

@irc.event("action")
def fed(connection,nickname,host,target,message):
	print(target+" "+nickname+"("+host+") "+message)

@irc.event("public")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+"("+host+"): "+message)

@irc.event("private")
def fed(connection,nickname,host,message):
	print(connection.nickname+" "+nickname+"("+host+"): "+message)
