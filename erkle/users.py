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

from erkle.decorator import irc
from erkle.common import *
from erkle.data import *

#--SINGLE_FILE--#

def handle_users(eobj,line):

	tokens = line.split()

	# OPER
	if tokens[1]=="381":
		irc.call("oper",eobj)
		return True

	# ENDOFWHOIS
	if tokens[1]=="318":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)

		if nickname in eobj._whois:
			whois = eobj._whois[nickname]
			irc.call("whois",eobj,whois)
			del eobj._whois[nickname]

		return True

	# WHOISUSER
	if tokens[1]=="311":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)
		username = tokens.pop(0)
		host = tokens.pop(0)

		tokens.pop(0)	# remove asterix

		realname = ' '.join(tokens)
		realname = realname [1:]

		eobj._whois[nickname] = WhoisData(nickname)
		eobj._whois[nickname].username = username
		eobj._whois[nickname].host = host
		eobj._whois[nickname].realname = realname

		return True

	# WHOISSERVER
	if tokens[1]=="312":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)

		server = tokens.pop(0)
		info = ' '.join(tokens)
		info = info[1:]

		if nickname in eobj._whois:
			eobj._whois[nickname].server = f"{server} ({info})"

		return True

	# WHOISOPERATOR
	if tokens[1]=="313":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)

		privs = ' '.join(tokens)
		privs = privs[1:]

		if nickname in eobj._whois:
			eobj._whois[nickname].privs = nickname + " " + privs

		return True

	# WHOISIDLE
	if tokens[1]=="317":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)

		idle = tokens.pop(0)
		signon = tokens.pop(0)

		try:
			idle = int(idle)
		except:
			idle = 0

		try:
			signon = int(signon)
		except:
			signon = 0

		if nickname in eobj._whois:
			eobj._whois[nickname].idle = idle
			eobj._whois[nickname].signon = signon

		return True

	# WHOISCHANNELS
	if tokens[1]=="319":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		nickname = tokens.pop(0)
		chans = ' '.join(tokens)
		chans = chans[1:]
		channel = chans.split(' ')

		if nickname in eobj._whois:
			eobj._whois[nickname].channels = channel
		return True

	# INVITE
	if tokens[1].lower()=="invite":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split("!")
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick

		channel = tokens.pop(0)
		channel = channel[1:]

		irc.call("invite",eobj,nickname,host,channel)
		return True

	# KICK
	if tokens[1].lower()=="kick":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split("!")
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove message type

		channel = tokens.pop(0)
		target = tokens.pop(0)

		msg = ' '.join(tokens)
		msg = msg[1:]
		if msg==nickname: msg = None

		if target==eobj.nickname:
			# client was the one kicked
			try:
				del eobj.users[channel]
			except:
				pass
			try:
				del eobj.topic[channel]
			except:
				pass
			irc.call("kicked",eobj,nickname,host,channel,msg)
		else:
			# other user kicked
			irc.call("kick",eobj,nickname,host,channel,target,msg)
			
			# Remove user from userlist
			cleaned = []
			for u in eobj.users[channel]:

				if u.nickname==target:
					continue

				cleaned.append(u)

			eobj.users[channel] = cleaned

			# Resend the new channel user list
			irc.call("names",eobj,channel,eobj.users[channel])

		return True

	# RPL_NOWAWAY
	if tokens[1]=="306":
		irc.call("away",eobj,self.nick,None)
		return True

	# RPL_UNAWAY
	if tokens[1]=="305":
		irc.call("back",eobj)
		return True

	# RPL_AWAY
	if tokens[1]=="301":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove client nickname

		user = tokens.pop(0)

		reason = " ".join(tokens)
		if len(reason)>0:
			reason = reason[1:]
		else:
			reason = None

		irc.call("away",eobj,user,reason)

		return True

	# NICK
	if tokens[1].lower()=="nick":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split("!")
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove msg type

		newnick = tokens.pop(0)
		newnick = newnick[1:]

		irc.call("nick",eobj,nickname,host,newnick)

		# Remove user from channel user lists
		for channel in eobj.users:
			cleaned = []
			found = False
			for cuser in eobj.users[channel]:

				if cuser.nickname==nickname:
					found = True
					cuser.nickname = nickname
					cleaned.append(cuser)
					continue

				cleaned.append(cuser)
			if found:
				eobj.users[channel] = cleaned
				# Resend the new channel user list
				irc.call("names",eobj,channel,eobj.users[channel])

		return True

	# QUIT
	if tokens[1].lower()=="quit":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split("!")
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove message type

		if len(tokens)>0:
			reason = " ".join(tokens)
			reason = reason[1:]
		else:
			reason = None

		irc.call("quit",eobj,nickname,host,reason)

		# Remove user from channel user lists
		for channel in eobj.users:
			cleaned = []
			found = False
			for cuser in eobj.users[channel]:

				if cuser.nickname==nickname:
					found = True
					continue

				cleaned.append(cuser)
			if found:
				eobj.users[channel] = cleaned
				# Resend the new channel user list
				irc.call("names",eobj,channel,eobj.users[channel])

		return True

	# PART
	if tokens[1].lower()=="part":
		hasreason = True
		if len(tokens)==3: hasreason = False

		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split("!")
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove message type

		channel = tokens.pop(0)

		if hasreason:
			reason = " ".join(tokens)
			reason = reason[1:]
		else:
			reason = ""

		if nickname == eobj.nickname:
			# client parted
			try:
				del eobj.users[channel]
			except:
				pass
			try:
				del eobj.topic[channel]
			except:
				pass
			irc.call("parted",eobj,channel)
			return

		irc.call("part",eobj,nickname,host,channel,reason)

		cleaned = []
		for u in eobj.users[channel]:
			if u.nickname==nickname: continue
			cleaned.append(u)
		eobj.users[channel] = cleaned

		# Resend the new channel user list
		irc.call("names",eobj,channel,eobj.users[channel])
		return True

	# User list end
	if tokens[1]=="366":
		channel = tokens[3]
		irc.call("names",eobj,channel,eobj.users[channel])
		return True

	# Incoming user list
	if tokens[1]=="353":
		data = line.split("=")

		parsed = data[1].split(':')
		channel = parsed[0].strip()
		users = parsed[1].split()

		# Generate user class objects
		pusers = []
		for u in users:
			user = parse_username(u)
			pusers.append(user)

		if channel in eobj.users:
			eobj.users[channel] = eobj.users[channel] + pusers
			eobj.users[channel] = clean_out_duplicate_users(eobj.users[channel])
			return True
		else:
			# eobj.users[channel] = users
			eobj.users[channel] = pusers
			return True

	# JOIN
	if tokens[1].lower()=="join":
		user = tokens[0]
		user = user[1:]
		channel = tokens[2]
		channel = channel[1:]

		p = user.split("!")
		nickname = p[0]
		host = p[1]

		if nickname==eobj.nickname:
			irc.call("joined",eobj,channel)
		else:
			irc.call("join",eobj,nickname,host,channel)

		if channel in eobj.users:
			eobj.users[channel].append( parse_username(user)  )
			eobj.users[channel] = clean_out_duplicate_users(eobj.users[channel])

		return True

	return False

#--SINGLE_FILE--#