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

from erkle.hooks import hook

def handle_users(eobj,line):

	tokens = line.split()

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
			del eobj.users[channel]
			hook.call("kicked",eobj,nickname,host,channel,msg)
		else:
			# other user kicked
			hook.call("kick",eobj,nickname,host,channel,target,msg)
			
			# Remove user from userlist
			cleaned = []
			for u in eobj.users[channel]:
				cu = u.replace('@','')
				cu = cu.replace('+','')
				cu = cu.replace('~','')
				cu = cu.replace('%','')
				cu = cu.replace('&','')

				parsed = cu.split('!')
				if len(parsed)==2:
					if parsed[0].lower()!=target.lower(): cleaned.append(u)
				else:
					if u.lower()!=target.lower(): cleaned.append(u)
			eobj.users[channel] = cleaned

			# Resend the new channel user list
			hook.call("names",eobj,channel,eobj.users[channel])

		return True

	# RPL_NOWAWAY
	if tokens[1]=="306":
		hook.call("away",eobj,self.nick,None)
		return True

	# RPL_UNAWAY
	if tokens[1]=="305":
		hook.call("back",eobj)
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

		hook.call("away",eobj,user,reason)

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

		hook.call("nick",eobj,nickname,host,newnick)

		# Remove user from channel user lists
		for channel in eobj.users:
			cleaned = []
			found = False
			for cuser in eobj.users[channel]:
				if cuser==nickname:
					found = True
					cleaned.append(newnick)
					continue
				if '@' in cuser:
					nuser = cuser.replace('@','')
					if nuser==nickname:
						found = True
						cleaned.append(f"@{newnick}")
						continue
				if '+' in cuser:
					nuser = cuser.replace('+','')
					if nuser==nickname:
						found = True
						cleaned.append(f"+{newnick}")
						continue
				if '~' in cuser:
					nuser = cuser.replace('~','')
					if nuser==nickname:
						found = True
						cleaned.append(f"~{newnick}")
						continue
				if '&' in cuser:
					nuser = cuser.replace('&','')
					if nuser==nickname:
						found = True
						cleaned.append(f"&{newnick}")
						continue
				if '%' in cuser:
					nuser = cuser.replace('%','')
					if nuser==nickname:
						found = True
						cleaned.append(f"%{newnick}")
						continue
				cleaned.append(cuser)
			if found:
				eobj.users[channel] = cleaned
				# Resend the new channel user list
				hook.call("names",eobj,channel,eobj.users[channel])

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

		hook.call("quit",eobj,nickname,host,reason)

		# Remove user from channel user lists
		for channel in eobj.users:
			cleaned = []
			found = False
			for cuser in eobj.users[channel]:
				if cuser==nickname:
					found = True
					continue
				if '@' in cuser:
					nuser = cuser.replace('@','')
					if nuser==nickname:
						found = True
						continue
				if '+' in cuser:
					nuser = cuser.replace('+','')
					if nuser==nickname:
						found = True
						continue
				if '~' in cuser:
					nuser = cuser.replace('~','')
					if nuser==nickname:
						found = True
						continue
				if '&' in cuser:
					nuser = cuser.replace('&','')
					if nuser==nickname:
						found = True
						continue
				if '%' in cuser:
					nuser = cuser.replace('%','')
					if nuser==nickname:
						found = True
						continue
				cleaned.append(cuser)
			if found:
				eobj.users[channel] = cleaned
				# Resend the new channel user list
				hook.call("names",eobj,channel,eobj.users[channel])

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

		hook.call("part",eobj,nickname,host,channel,reason)

		# Remove user from channel user list
		cleaned = []
		for cuser in eobj.users[channel]:
			if cuser==nickname: continue
			if '@' in cuser:
				nuser = cuser.replace('@','')
				if nuser==nickname: continue
			if '+' in cuser:
				nuser = cuser.replace('+','')
				if nuser==nickname: continue
			if '~' in cuser:
				nuser = cuser.replace('~','')
				if nuser==nickname: continue
			if '&' in cuser:
				nuser = cuser.replace('&','')
				if nuser==nickname: continue
			if '%' in cuser:
				nuser = cuser.replace('%','')
				if nuser==nickname: continue
			cleaned.append(cuser)
		eobj.users[channel] = cleaned

		# Resend the new channel user list
		hook.call("names",eobj,channel,eobj.users[channel])
		return True

	# User list end
	if tokens[1]=="366":
		channel = tokens[3]
		hook.call("names",eobj,channel,eobj.users[channel])
		return True

	# Incoming user list
	if tokens[1]=="353":
		data = line.split("=")

		parsed = data[1].split(':')
		channel = parsed[0].strip()
		users = parsed[1].split()

		if channel in eobj.users:
			eobj.users[channel] = eobj.users[channel] + users
			eobj.users[channel] = list(dict.fromkeys(eobj.users[channel]))
			return True
		else:
			eobj.users[channel] = users
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

		hook.call("join",eobj,nickname,host,channel)

		if channel in eobj.users:
			eobj.users[channel].append(user)
			eobj.users[channel] = list(dict.fromkeys(eobj.users[channel]))

		return True

	return False