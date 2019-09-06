# MIT License

# Copyright (c) 2019 Dan Hetrick

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from erkle import *

@hook.event("list")
def evlist(connection,chanlist):
	print("Begin channel list for "+connection.server+":"+str(connection.port))
	for e in chanlist:
		if e[1]>1:
			numusers = str(e[1])+" users"
		else:
			numusers = str(e[1])+" user"
		if e[2]:
			print(e[0]+" ("+numusers+") - "+e[2])
		else:
			print(e[0]+" ("+numusers+")")
	print("End channel list")

@hook.event("whois")
def evwhois(connection,nickname,user,host,realname,server,idle,signon,channels,privs):
	print(f"{nickname} {user}@{host} ({realname})")
	print(f"{nickname} is connected to {server}")
	print(f"{nickname} has been {str(idle)} for idle second(s)")
	print(f"{nickname} connected on {signon}")
	if len(channels)>0: print(f"{nickname} is in {','.join(channels)}")
	if privs:
		print(privs)

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
