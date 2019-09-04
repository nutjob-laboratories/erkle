from erkle import *

@hook.event("notice")
def ntc(connection,sender,message):
	print("notice: "+sender+": "+message)

@hook.event("action")
def fed(connection,nickname,host,target,message):
	print(target+" "+nickname+"("+host+") "+message)

@hook.event("public")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+"("+host+"): "+message)

@hook.event("private")
def fed(connection,nickname,host,message):
	print(connection.nickname+" "+nickname+"("+host+"): "+message)
