
from erkle.hooks import hook

def handle_users(eobj,line):

	tokens = line.split()

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
		return

	# Incoming user list
	if tokens[1]=="353":
		data = line.split("=")

		parsed = data[1].split(':')
		channel = parsed[0].strip()
		users = parsed[1].split()

		if channel in eobj.users:
			eobj.users[channel] = eobj.users + users
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
		return True

	return False