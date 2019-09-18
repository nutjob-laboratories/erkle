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

@irc.event("error", "erkle.events.dump")
def everr(connection,code,target,reason):
	if target!=None:
		print("ERROR: "+code+" "+target+" - "+reason)
	else:
		print("ERROR: "+code+" - "+reason)

@irc.event("list", "erkle.events.dump")
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

@irc.event("whois", "erkle.events.dump")
def evwhois(connection,whois):
	print(f"{whois.nickname} {whois.username}@{whois.host} ({whois.realname})")
	print(f"{whois.nickname} is connected to {whois.server}")
	print(f"{whois.nickname} has been {str(whois.idle)} for idle second(s)")
	print(f"{whois.nickname} connected on {whois.signon}")
	if len(whois.channels)>0: print(f"{whois.nickname} is in {','.join(whois.channels)}")
	if whois.privs:
		print(whois.privs)

@irc.event('kick', "erkle.events.dump")
def evkick(connection,nickname,host,channel,target,message):
	if message:
		print(nickname+"("+host+") "+" kicked "+target+" from "+channel+": "+message)
	else:
		print(nickname+"("+host+") "+" kicked "+target+" from "+channel)

@irc.event('kicked', "erkle.events.dump")
def evkick(connection,nickname,host,channel,message):
	if message:
		print(nickname+"("+host+") "+" kicked you from "+channel+": "+message)
	else:
		print(nickname+"("+host+") "+" kicked you from "+channel)

@irc.event('mode', "erkle.events.dump")
def evmode(connection,nickname,host,target,mode):
	print(nickname+" set mode "+mode+" on "+target)

@irc.event('topic', "erkle.events.dump")
def evtopic(connection,nickname,host,channel,topic):
	if topic:
		print(nickname+"("+host+") "+" set the topic in "+channel+" to "+topic)
	else:
		print(nickname+"("+host+") "+" set the topic in "+channel+" to nothing")

@irc.event("back", "erkle.events.dump")
def evb(connection):
	print("You are back")

@irc.event("away", "erkle.events.dump")
def awy(connection,nickname,reason):
	if nickname==connection.nickname:
		print("You have been set as away")
	else:
		if reason:
			print(nickname+" is away ("+reason+")")
		else:
			print(nickname+" is away")

@irc.event("notice", "erkle.events.dump")
def ntc(connection,sender,message):
	print("notice: "+sender+": "+message)

@irc.event("motd", "erkle.events.dump")
def mt(connection,motd):
	print(motd)

@irc.event("registered", "erkle.events.dump")
def con(connection):
	print("Registered with "+connection.server+":"+str(connection.port))

@irc.event("connect", "erkle.events.dump")
def bla(connection):
	print("Connected to "+connection.server+":"+str(connection.port))

@irc.event("nick-taken", "erkle.events.dump")
def glarp(connection,newnick):
	print("Your nick was changed to "+newnick)

@irc.event("action", "erkle.events.dump")
def fed(connection,nickname,host,target,message):
	print(target+" "+nickname+"("+host+") "+message)

@irc.event("public", "erkle.events.dump")
def fed(connection,nickname,host,channel,message):
	print(channel+" "+nickname+"("+host+"): "+message)

@irc.event("private", "erkle.events.dump")
def fed(connection,nickname,host,message):
	print(connection.nickname+" "+nickname+"("+host+"): "+message)

@irc.event("ping", "erkle.events.dump")
def png(connection):
	print("Ping? Pong!")

@irc.event("nick", "erkle.events.dump")
def ni(connection,nickname,host,newnick):
	print(nickname+"("+host+") "+" is now known as "+newnick)

@irc.event("names", "erkle.events.dump")
def evn(connection,channel,userlist):
	#print(channel+" "+",".join(userlist))
	ul = []
	for u in userlist:
		us = ''
		if u.op: us = us + '@'
		if u.voiced: us = us + '+'
		if u.owner: us = us + '~'
		if u.halfop: us = us + '%'
		if u.admin: us = us + '&'
		us = us + u.nickname
		ul.append(us)

	print(channel+" "+",".join(ul))

@irc.event("quit", "erkle.events.dump")
def evq(connection,nickname,host,reason):
	if reason:
		print(nickname+"("+host+") "+" quit ("+reason+")")
	else:
		print(nickname+"("+host+") "+" quit")

@irc.event("part", "erkle.events.dump")
def evp(connection,nickname,host,channel,reason):
	if reason:
		print(nickname+"("+host+") left "+channel+" ("+reason+")")
	else:
		print(nickname+"("+host+") left "+channel)

@irc.event("parted", "erkle.events.dump")
def evp(connection,channel):
	print("You left "+channel)

@irc.event("join", "erkle.events.dump")
def evj(connection,nickname,host,channel):
	print(nickname+"("+host+") joined "+channel)

@irc.event("joined", "erkle.events.dump")
def evj(connection,channel):
	print("You joined "+channel)
