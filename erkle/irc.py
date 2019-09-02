
import socket
import sys
from collections import defaultdict

SSL_AVAILABLE = True
try:
	import ssl
except ImportError:
	SSL_AVAILABLE = False

from erkle.hooks import hook
from erkle.options import handle_options
from erkle.users import handle_users

class ErkleClient:

	"""
		send

		Sends a message to the IRC server
	"""
	def send(self,data):
		self.connection.send(bytes(data + "\r\n", "utf-8"))

	def join(self,channel,key=None):
		if key:
			self.send("JOIN "+channel+" "+key)
		else:
			self.send("JOIN "+channel)

	def part(self,channel,reason=None):
		if reason:
			self.send("PART "+channel+" "+reason)
		else:
			self.send("PART "+channel)

	def quit(self,reason=None):
		if reason:
			self.send("QUIT")
		else:
			self.send("QUIT "+reason)

	def msg(self,target,msg):
		self.send("PRIVMSG "+target+" "+msg)

	def action(self,target,msg):
		self.send("PRIVMSG "+target+" \x01ACTION"+msg+"\x01")

	def notice(self,target,msg):
		self.send("NOTICE "+target+" "+msg)

	def __init__(self,nickname,username,realname,server,port=6667,password="",usessl=False):
		self.nickname = nickname
		self.username = username
		self.realname = realname
		self.server = server
		self.port = port
		self.password = password
		self.usessl = usessl

		self.current_nickname = nickname

		# If SSL isn't available, set self.usessl to false
		if not SSL_AVAILABLE:
			self.usessl = False

		self._buffer = ""	# Where incoming server data is stored

		self.hostname = ""				# The server's hostname
		self.software = ""				# The server's software
		self.options = []				# The server's options
		self.network = ""				# The IRC server's network
		self.commands = []				# Commands the server supports
		self.maxchannels = 0			# Maximum number of channels
		self.maxnicklen = 0				# Maximum nick length
		self.chanlimit = []				# Server channel limit
		self.nicklen = 0				# Server nick length
		self.chanellen = 0				# Server channel name length
		self.topiclen = 0				# Server channel topic length
		self.kicklen = 0				# Server kick length
		self.awaylen = 0				# Server away length
		self.maxtargets = 0				# Server maximum msg targets
		self.modes = 0					# Server maximum channel modes
		self.chantypes = []				# What channel types the server uses
		self.prefix = []				# Server status prefixes
		self.chanmodes = []				# What channel modes the server uses
		self.casemapping = ""			# Server case mapping
		self.spoofed = ""				# The client's spoofed host

		self.users = defaultdict(list)	# List of channel users

		self.topic = {}					# Channel topics

	def connect(self):
		self.run()

	def run(self):

		hook.call("start",self)

		""" Create the server socket and connect"""
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.connection.connect((self.server,self.port))

		""" SSL-ify the server socket if needed"""
		if self.usessl:
			self.connection = ssl.wrap_socket(self.connection)

		hook.call("connect",self)

		# Get the server to send nicks/hostmasks
		self.send("PROTOCTL UHNAMES")

		""" Send the server password, if there is one"""
		if self.password:
			self.send(f"PASS {self.password}")

		""" Send user information to the server"""
		self.send(f"NICK {self.nickname}")
		self.send(f"USER {self.username} 0 0 :{self.realname}")

		""" Begin the connection loop """
		self._buffer = ""
		while True:
			""" Get incoming sercer data """
			try:
				self._buffer = self._buffer + self.connection.recv(4096).decode("utf-8")
			except socket.error:
				pass

			while True:
				newline = self._buffer.find("\n")
				if newline == -1:
					break

				line = self._buffer[:newline]
				self._buffer = self._buffer[newline+1:]

				hook.call("line",self,line)
				self.handle(line)

	def handle(self,line):

		tokens = line.split()

		# Server options
		if handle_options(self,line): return

		# User management
		if handle_users(self,line): return

		# Return server ping
		if tokens[0].lower()=="ping":
			self.send("PONG " + tokens[1])
			hook.call("ping",self)
			return

		# Nick collision
		if tokens[1]=="433":
			if self.current_nickname==self.nickname:
				# Use alternate nick
				self.nickname = self.nickname + "_"
				self.current_nickname = self.nickname
				self.send(f"NICK {self.nickname}")
				hook.call("nick-taken",self,self.nickname)
				return

		# Server welcome
		if tokens[1]=="001":
			hook.call("welcome",self)
			return

		# Chat message
		if tokens[1].lower()=="privmsg":
			userhost = tokens.pop(0)
			userhost = userhost[1:]
			tokens.pop(0)
			target = tokens.pop(0)
			message = ' '.join(tokens)
			message = message[1:]
			
			p = userhost.split('!')
			nickname = p[0]
			host = p[1]

			# CTCP action
			if "\x01ACTION" in message:
				message = message.replace("\x01ACTION",'')
				message = message[:-1]
				message = message.strip()
				hook.call("action",self,nickname,host,target,message)
				return

			if target.lower()==self.nickname.lower():
				# private message
				hook.call("private",self,nickname,host,message)
				return
			else:
				# public message
				hook.call("public",self,nickname,host,target,message)
				return

		# Notice messages
		if tokens[1].lower()=="notice":
			tokens.pop(0)	# remove server
			tokens.pop(0)	# remove message type

			parsed = " ".join(tokens).split(":")
			sender = parsed[0].strip()
			message = parsed[1].strip()
			hook.call("notice",self,sender,message)
			return

