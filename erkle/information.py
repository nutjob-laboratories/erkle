
from erkle.hooks import hook

def handle_information(eobj,line):

	tokens = line.split()
	#print(line)

	if tokens[1].lower()=="mode":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split('!')
		if len(parsed)==2:
			nickname = parsed[0]
			host = parsed[1]
		else:
			nickname = eobj.hostname
			host = eobj.hostname

		tokens.pop(0)	# remove message type

		target = tokens.pop(0)

		mode = ' '.join(tokens)
		mode = mode.replace(':','',1)

		hook.call("mode",eobj,nickname,host,target,mode)

		return True

	# chanmodeis
	if tokens[1]=="324":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type

		channel = tokens.pop(0)
		mode = ' '.join(tokens)
		mode = mode.replace(':','',1)

		hook.call("mode",eobj,eobj.hostname,eobj.hostname,target,mode)
		return True

	if tokens[1].lower()=="topic":
		user = tokens.pop(0)
		user = user[1:]

		parsed = user.split('!')
		nickname = parsed[0]
		host = parsed[1]

		tokens.pop(0)	# remove message type

		channel = tokens.pop(0)

		topic = ' '.join(tokens)
		topic = topic[1:]

		if not len(topic)>0: topic = None

		eobj.topic[channel] = topic
		hook.call("topic",eobj,nickname,host,channel,topic)

		return True

	# 331 no topic
	if tokens[1]=="331":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nickname

		channel = tokens.pop(0)

		eobj.topic[channel] = ''
		hook.call("topic",eobj,eobj.hostname,eobj.hostname,channel,None)
		return True

	# 332 topic
	if tokens[1]=="332":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nickname

		channel = tokens.pop(0)

		topic = " ".join(tokens)
		topic = topic[1:]

		if len(topic)>0:
			eobj.topic[channel] = topic
			hook.call("topic",eobj,eobj.hostname,eobj.hostname,channel,topic)
		else:
			eobj.topic[channel] = ''
			hook.call("topic",eobj,eobj.hostname,eobj.hostname,channel,None)
		return True

	# 396
	if tokens[1]=="396":
		eobj.spoofed = tokens[3]
		return True

	# 004
	if tokens[1]=="004":
		eobj.hostname = tokens[3]
		eobj.software = tokens[4]
		return True

	# MOTD begins
	if tokens[1]=="375":
		eobj.motd = []
		return True

	# MOTD content
	if tokens[1]=="372":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nickname
		data = " ".join(tokens)
		data = data[3:]
		data = data.strip()
		eobj.motd.append(data)
		return True

	# MOTD ends
	if tokens[1]=="376":
		motd = "\n".join(eobj.motd)
		motd = motd.strip()
		hook.call("motd",eobj,motd)
		return True

	# 005
	if tokens[1]=="005":
		tokens.pop(0)	# remove server
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nick
		for ent in tokens:
			if ":" in ent:
				# no more options in the list sent
				break
			if '=' in ent:
				parsed = ent.split('=')

				if parsed[0].lower()=="casemapping":
					eobj.casemapping=parsed[1]
					continue

				if parsed[0].lower()=="chanmodes":
					eobj.chanmodes = parsed[1].split(',')
					continue

				if parsed[0].lower()=="prefix":
					data = parsed[1].split(")")
					data[0] = data[0][1:]

					plevels = data[0].split()
					psymbols = data[1].split()

					table = []
					counter = 0
					for p in plevels:
						ent = [p,psymbols[counter]]
						table.append(ent)
						counter = counter + 1

					eobj.prefix = table

					continue

				if parsed[0].lower()=="chantypes":
					eobj.chantypes = parsed[1].split(',')
					continue
				if parsed[0].lower()=="modes":
					eobj.modes=int(parsed[1])
					continue
				if parsed[0].lower()=="maxtargets":
					eobj.maxtargets=int(parsed[1])
					continue
				if parsed[0].lower()=="awaylen":
					eobj.awaylen=int(parsed[1])
					continue
				if parsed[0].lower()=="kicklen":
					eobj.kicklen=int(parsed[1])
					continue
				if parsed[0].lower()=="topiclen":
					eobj.topiclen=int(parsed[1])
					continue
				if parsed[0].lower()=="chanellen":
					eobj.chanellen=int(parsed[1])
					continue
				if parsed[0].lower()=="nicklen":
					eobj.nicklen=int(parsed[1])
					continue
				if parsed[0].lower()=="chanlimit":
					eobj.chanlimit = parsed[1].split(',')
					continue
				if parsed[0].lower()=="maxnicklen":
					eobj.maxnicklen=int(parsed[1])
					continue
				if parsed[0].lower()=="maxchannels":
					eobj.maxchannels=int(parsed[1])
					continue
				if parsed[0].lower()=="network":
					eobj.network = parsed[1]
					continue
				if parsed[0].lower()=="cmds":
					eobj.commands = parsed[1].split(',')
					continue
			eobj.options.append(ent)
		return True
	return False
