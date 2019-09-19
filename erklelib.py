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

import socket
from collections import defaultdict
import string
import sys
import threading
import os

SSL_AVAILABLE = True
try:
	import ssl
except ImportError:
	SSL_AVAILABLE = False

__all__ = ['irc','Erkle','ERKLE_VERSION']


APPLICATION_NAME = "Erkle"
ERKLE_VERSION = "0.043"

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " IRC Client"

NO_NICKNAME_IN_DICT_ERROR = "Key 'nickname' missing from configuration dict."
NO_SERVER_IN_DICT_ERROR = "Key 'server' missing from configuration dict."
NO_SSL_ERROR = "SSL/TLS is not available. Please install pyOpenSSL."
DISCONNECTED_ERROR = "Disconnected from the server."
SEND_MESSAGE_ERROR = "Cannot send message: disconnected from the server."
NOT_STARTED_MESSAGE_ERROR = "Connection not started; can't send message '{}'"
NOT_THREADED_ERROR = "Connection was not started with spawn()! Exiting..."
NO_SOCKET_ERROR = "Socket has not been created, connection has not been started."
NOT_STARTED_ERROR = "Connection not started."
WRONG_VARIABLE_TYPE = "Wrong variable type for '{key}' (received {rec}, expected {exp})."
CANNOT_ADD_ASTERIX_TAG = "'*' is not a valid tag name."
CANNOT_REMOVE_ASTERIX_TAG = "Can't remove '*' tag (not a valid tag)."
UNKNOWN_ERROR = "Unknown error"


class Event:
	def __init__(self,func,tags):
		self.function = func
		self.tags = tags

class EventHandler:
	def __init__(self):
		self._handlers = {}
		self._disabled = []

	def call(self,event,eobj,*args):
		if event in self._handlers:
			for h in self._handlers[event]:
				# h(*args)

				# Check to see if the Erkle object has any tags
				DOIT = True
				if len(eobj.tags)>0:
					# See if the hooked function has the Erkle object's tag
					DOIT = False
					for t in eobj.tags:
						# The hooked function has the Erkle object's tag
						if t in h.tags: DOIT = True
					if '*' in h.tags: DOIT = True

				nogo = False
				for t in h.tags:
					if t in self._disabled: nogo=True
				if not nogo:
					if DOIT: h.function(eobj,*args)

	def event(self, event, *args):
		def registerhandler(handler):
			tags = []
			for t in args:
				tags.append(t)

			if event in self._handlers:
				#self._handlers[event].append(handler)
				ef = Event(handler,tags)
				self._handlers[event].append(ef)
			else:
				# self._handlers[event] = [handler]
				ef = Event(handler,tags)
				self._handlers[event] = [ef]
			return handler
		return registerhandler

irc = EventHandler()


class Erkle:

	# __init__()
	# Arguments: dict
	#
	# Initializes an Erkle() object.
	def __init__(self,serverinfo):

		self.nickname = None
		if 'nickname' in serverinfo:
			self.nickname = serverinfo['nickname']
		if 'nick' in serverinfo:
			self.nickname = serverinfo['nick']
		if self.nickname == None:
			self._display_error_and_exit(NO_NICKNAME_IN_DICT_ERROR)

		if 'server' in serverinfo:
			self.server = serverinfo['server']
		else:
			self._display_error_and_exit(NO_SERVER_IN_DICT_ERROR)

		self.username = self.nickname
		if 'username' in serverinfo:
			self.username = serverinfo['username']
		if 'user' in serverinfo:
			self.username = serverinfo['user']

		self.realname = DEFAULT_REALNAME
		if 'realname' in serverinfo:
			self.realname = serverinfo['realname']
		if 'real' in serverinfo:
			self.realname = serverinfo['real']

		self.alternate = self.nickname + "_"
		if 'alternate' in serverinfo:
			self.alternate = serverinfo['alternate']
		if 'alt' in serverinfo:
			self.alternate = serverinfo['alt']

		if 'port' in serverinfo:
			self.port = serverinfo['port']
		else:
			self.port = 6667

		if 'password' in serverinfo:
			self.password = serverinfo['password']
		else:
			self.password = None

		if 'ssl' in serverinfo:
			self.usessl = serverinfo['ssl']
		else:
			self.usessl = False

		if 'encoding' in serverinfo:
			self.encoding = serverinfo['encoding']
		else:
			self.encoding = "utf-8"

		if 'flood-protection' in serverinfo:
			self.flood_protection = serverinfo['flood-protection']
		else:
			self.flood_protection = True

		if 'flood-rate' in serverinfo:
			self.floodrate = serverinfo['flood-rate']
		else:
			self.floodrate = 2

		if 'clock-frequency' in serverinfo:
			self._clock_resolution = serverinfo['clock-frequency']
		else:
			self._clock_resolution = 1.0

		if 'multithreaded' in serverinfo:
			self._multithreaded = serverinfo['multithreaded']
		else:
			self._multithreaded = False

		self.show_input = False
		if 'show-input' in serverinfo:
			self.show_input = serverinfo['show-input']

		self.show_output = False
		if 'show-output' in serverinfo:
			self.show_output = serverinfo['show-output']

		# Check to make sure all config input is the right variable type
		self._check_configuration_input_type('nickname',self.nickname,str())
		self._check_configuration_input_type('username',self.username,str())
		self._check_configuration_input_type('realname',self.realname,str())
		self._check_configuration_input_type('alternate',self.alternate,str())
		self._check_configuration_input_type('server',self.server,str())
		self._check_configuration_input_type('port',self.port,int())
		self._check_configuration_input_type('ssl',self.usessl,bool())
		self._check_configuration_input_type('encoding',self.encoding,str())
		self._check_configuration_input_type('flood-protection',self.flood_protection,bool())
		self._check_configuration_input_type('flood-rate',self.floodrate,int())
		self._check_configuration_input_type('clock-frequency',self._clock_resolution,float())
		self._check_configuration_input_type('multithreaded',self._multithreaded,bool())
		self._check_configuration_input_type('show-input',self.show_input,bool())
		self._check_configuration_input_type('show-output',self.show_output,bool())

		# Check to make sure that the password (if there is one) is a string
		if self.password!=None:
			if type(self.password)!=type(str):

				if type(var)==type(str()):
					intype = "string"
				elif type(var)==type(int()):
					intype = "integer"
				elif type(var)==type(float()):
					intype = "float"
				elif type(var)==type(bool()):
					intype = "boolean"
				else:
					intype = 'unknown'

				print("ERROR: "+WRONG_VARIABLE_TYPE.format(key='password',rec=intype,exp='string'))
				sys.exit(1)

		# If SSL isn't available, and SSL is set to
		# be used, raise an error
		if not SSL_AVAILABLE:
			if self.usessl:
				self._display_error_and_exit(NO_SSL_ERROR)

		self._buffer = ""						# Incoming data buffer
		self._channels = []						# Channel list buffer
		self._thread = None						# If multithreaded, stores the object's thread
		self._whois = {}						# WHOIS data buffer
		self._message_queue = []				# Outgoing message queue for flood protection
		self._last_message_time = 0				# The time the last message was sent to the server
		self._started = False					# Stores if the IRC connection has been started or not
		self._current_nickname = self.nickname	# Stores the current nickname (for 433 errors)

		self.hostname = ""							# The server's hostname
		self.software = ""							# The server's software
		self.options = []							# The server's options
		self.network = ""							# The IRC server's network
		self.commands = []							# Commands the server supports
		self.maxchannels = 0						# Maximum number of channels
		self.maxnicklen = 0							# Maximum nick length
		self.chanlimit = []							# Server channel limit
		self.nicklen = 0							# Server nick length
		self.chanellen = 0							# Server channel name length
		self.topiclen = 0							# Server channel topic length
		self.kicklen = 0							# Server kick length
		self.awaylen = 0							# Server away length
		self.maxtargets = 0							# Server maximum msg targets
		self.modes = 0								# Server maximum channel modes
		self.chantypes = []							# What channel types the server uses
		self.prefix = []							# Server status prefixes
		self.chanmodes = []							# What channel modes the server uses
		self.casemapping = ""						# Server case mapping
		self.spoofed = ""							# The client's spoofed host
		self.users = defaultdict(list)				# List of channel users
		self.topic = {}								# Channel topics
		self.channels = []							# Server channel list
		self.tags = []								# Object tags
		self.uptime = 0								# Object uptime, in seconds
		self.multithreaded = self._multithreaded	# If the object is multithreaded or not

	# _run()
	# Arguments: none
	#
	# Connects to IRC and starts the loop that receives messages from the server
	# and handles them.
	def _run(self):

		# Create "stop clocks" event
		self._stop_clocks = threading.Event()

		# Start the uptime clock
		self._uptime_clock = Uptimer(self._stop_clocks,self)
		self._uptime_clock.start()

		# Start the tick clock
		self._regular_clock = Clock(self._stop_clocks,self)
		self._regular_clock.start()

		# Set object state as "started"
		self._started = True

		# Raise the "start" event
		irc.call("connecting",self)

		# Create the connection socket and connect to the server
		self._client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self._client.connect((self.server,self.port))

		## SSL-ify the connection if needed
		if self.usessl:
			self._client = ssl.wrap_socket(self._client)

		# Raise the "connect" event
		irc.call("connect",self)

		# Get the server to send nicks/hostmasks and all status symbols
		self._send("PROTOCTL UHNAMES NAMESX")

		# Send server password, if necessary
		if self.password:
			self._send(f"PASS {self.password}")

		# Send user information
		self._send(f"NICK {self.nickname}")
		self._send(f"USER {self.username} 0 0 :{self.realname}")

		# Begin the connection loop
		self._buffer = ""
		while True:
			try:
				# Get incoming server data
				line = self._client.recv(4096)

				# Decode incoming server data
				try:
					# Attempt to decode with the selected encoding
					line2 = line.decode(self.encoding)
				except UnicodeDecodeError:
					try:
						# Attempt to decode with "latin1"
						line2 = line.decode('iso-8859-1')
					except UnicodeDecodeError:
						# Finally, if nothing else works, use windows default encoding
						line2 = line.decode("CP1252", 'replace')
				# Add incoming data to the internal buffer
				self._buffer = self._buffer + line2
			except socket.error:
				print(DISCONNECTED_ERROR)

				# Stop timers
				self._stop_clocks.set()

				# Shutdown the connection
				self._client.shutdown(socket.SHUT_RDWR)
				self._client.close()
				return

			# Step through the buffer and look for newlines
			while True:
				newline = self._buffer.find("\n")

				# Newline not found, so we'll break and wait for more incoming data
				if newline == -1:
					break

				# Grab the incoming line
				line = self._buffer[:newline]

				# Remove the incoming line from the buffer
				self._buffer = self._buffer[newline+1:]

				# Raise the "line" event
				irc.call("line",self,line)

				# Handle the line
				self._handle(line)

				if self.show_input: print("<- "+line)

	# _handle()
	# Arguments: string
	#
	# Parses IRC messages from the server, and triggers events
	def _handle(self,line):

		tokens = line.split()

		# Return server ping
		if tokens[0].lower()=="ping":
			self._send("PONG " + tokens[1])
			irc.call("ping",self)
			return

		# Nick collision
		if tokens[1]=="433":
			if self._current_nickname==self.nickname:
				# Use alternate nick
				if self.nickname == self.alternate:
					self.nickname = self.nickname + "_"
					self._current_nickname = self.nickname
					self._send(f"NICK {self.nickname}")
				else:
					self.nickname = self.alternate
					self._current_nickname = self.alternate
					self._send(f"NICK {self.alternate}")
				irc.call("nick-taken",self,self.nickname)
				return

		# Server welcome
		if tokens[1]=="001":
			irc.call("registered",self)
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
				irc.call("action",self,nickname,host,target,message)
				return

			if target.lower()==self.nickname.lower():
				# private message
				irc.call("private",self,nickname,host,message)
				return
			else:
				# public message
				irc.call("public",self,nickname,host,target,message)
				return

		# Notice messages
		if tokens[1].lower()=="notice":
			tokens.pop(0)	# remove server
			tokens.pop(0)	# remove message type

			parsed = " ".join(tokens).split(":")
			sender = parsed[0].strip()
			message = parsed[1].strip()
			irc.call("notice",self,sender,message)
			return

		# Error management
		if handle_errors(self,line): return

		# Server options
		if handle_information(self,line): return

		# User management
		if handle_users(self,line): return

	# _regular_clock_tick()
	# Arguments: none
	#
	# Executes every X seconds (set by the clock-frequency setting)
	def _regular_clock_tick(self):
		irc.call("tick",self)

	# _uptime_clock_tick()
	# Arguments: none
	#
	# Increments the uptime by one second, and calls
	# _sendqueue() to send queued messages.
	def _uptime_clock_tick(self):
		# self.uptime = self.uptime + 1
		self.uptime = self.uptime + 1

		if self.flood_protection:
			if (self.uptime % self.floodrate)==0:
				self._sendqueue()

	# _not_started()
	# Arguments: None
	#
	# Returns false if the object is connected (or has
	# started connecting) to an IRC  server
	def _not_started(self):
		if self._started:
			return False
		else:
			return True

	# _check_configuration_input_type()
	# Arguments: string, variuable, variable type
	#
	# Checks to make sure a configuration input is
	# the proper variable type; display an error and
	# exit if it isn't
	def _check_configuration_input_type(self,cname,var,typ):
		if type(var)!=type(typ):

			if type(var)==type(str()):
				intype = "string"
			elif type(var)==type(int()):
				intype = "integer"
			elif type(var)==type(float()):
				intype = "float"
			elif type(var)==type(bool()):
				intype = "boolean"
			else:
				intype = 'unknown'

			if type(typ)==type(str()):
				reqtype = "string"
			elif type(typ)==type(int()):
				reqtype = "integer"
			elif type(typ)==type(float()):
				reqtype = "float"
			elif type(typ)==type(bool()):
				reqtype = "boolean"
			else:
				reqtype = 'unknown'

			print("ERROR: "+WRONG_VARIABLE_TYPE.format(key=cname,rec=intype,exp=reqtype))
			sys.exit(1)

	# _display_error_and_exit()
	# Arguments: string
	#
	# Displays an error message and exits
	def _display_error_and_exit(self,msg):
		print("ERROR: "+msg)
		sys.exit(1)

	# _raise_runtime_error()
	# Arguments: string
	#
	# Raises a runtime error
	def _raise_runtime_error(self,msg):
		raise RuntimeError(msg)

	# _sendqueue()
	# Arguments: none
	#
	# Removes a single message from the message queue
	# and sends it to the IRC server.
	def _sendqueue(self):
		if len(self._message_queue)>0:
			msg = self._message_queue.pop(0)
			self._send(msg)
			self._last_message_time = self.uptime

	# _send()
	# Arguments: string
	#
	# Sends a message to the IRC server
	def _send(self,data):

		if self.show_output: print("-> "+data)

		sender = getattr(self._client, 'write', self._client.send)
		try:
			sender(bytes(data + "\r\n", self.encoding))
		except socket.error:
			print(SEND_MESSAGE_ERROR)

			# Shutdown the connection and exit
			self._client.shutdown(socket.SHUT_RDWR)
			self._client.close()
			sys.exit(1)

	# tag()
	# Arguments: string[, string,...]
	#
	# Adds a tag to the Erkle object
	def tag(self,*args):
		for t in args:
			if t=='*': self._raise_runtime_error(CANNOT_ADD_ASTERIX_TAG)
			self.tags.append(t)
			irc._disabled = list(dict.fromkeys(irc._disabled))

	# untag()
	# Arguments: string[, string,...]
	#
	# Removes a tag from the Erkle object
	def untag(self,*args):
		for t in args:
			if t=='*': self._raise_runtime_error(CANNOT_REMOVE_ASTERIX_TAG)
			try:
				self.tags.remove(t)
			except:
				pass

	# enable()
	# Arguments: string[, string,...]
	#
	# Enables a disabled event tag
	def enable(self,*args):
		for tag in args:
			try:
				irc._disabled.remove(tag)
			except:
				pass

	# disabled()
	# Arguments: string[, string,...]
	#
	# Disables events with the given tag(s)
	def disable(self,*args):
		for tag in args:
			irc._disabled.append(tag)
			irc._disabled = list(dict.fromkeys(irc._disabled))

	# connect()
	# Arguments: none
	#
	# Calls _run().
	def connect(self):
		if self._multithreaded:
			t = threading.Thread(name=f"{self.server}:{str(self.port)}",target=self._run)
			self._thread = t
			t.start()
		else:
			self._run()

	# thread()
	# Arguments: none
	#
	# Returns the objects thread, or None if the object isn't threaded
	def thread(self):
		return self._thread

	# kill()
	# Arguments: none
	#
	# Terminates the thread, if the object is threaded
	def kill(self):

		if self._not_started():
			self._raise_runtime_error(NOT_STARTED_ERROR)

		# Stop timers
		self._stop_clocks.set()

		if self._thread != None:
			sys.exit()
		else:
			self._raise_runtime_error(NOT_THREADED_ERROR)

	# socket()
	# Arguments: none
	#
	# Returns the object's socket
	def socket(self):
		if self._not_started():
			self._raise_runtime_error(NO_SOCKET_ERROR)
		else:
			return self._client

	# send()
	# Arguments: string
	#
	# If flood protection is turned on, adds a message
	# to the outgoing message queue. If flood protection
	# is turned off, directly sends a message to
	# the IRC server.
	def send(self,data):

		if self._not_started():
			self._raise_runtime_error(NOT_STARTED_MESSAGE_ERROR.format(data))

		if self.flood_protection:
			if (self._last_message_time + self.floodrate) <= self.uptime:
				self._last_message_time = self.uptime
				self._send(data)
			else:
				self._message_queue.append(data)
		else:
			self._send(data)

	# oper()
	# Arguments: string, string
	#
	# Sends a OPER command to the IRC server
	def oper(self,username,password):
		self.send("OPER "+username+" "+password)

	# join()
	# Arguments: string, string
	#
	# Sends a JOIN command to the IRC server
	def join(self,channel,key=None):
		if key:
			self.send("JOIN "+channel+" "+key)
		else:
			self.send("JOIN "+channel)

	# part()
	# Arguments: string, string
	#
	# Sends a PART command to the IRC server
	def part(self,channel,reason=None):
		if reason:
			self.send("PART "+channel+" "+reason)
		else:
			self.send("PART "+channel)

	# quit()
	# Arguments: string
	#
	# Sends a QUIT command to the IRC server
	def quit(self,reason=''):
		if reason=='':
			self.send("QUIT")
		else:
			self.send("QUIT "+reason)
		self._client.shutdown(socket.SHUT_RDWR)
		self._client.close()

		# Stop timers
		self._stop_clocks.set()

		# Exit the thread, if we're running in a thread
		if self._thread != None: sys.exit()

	# privmsg()
	# Arguments: string, string
	#
	# Sends a PRIVMSG command to the IRC server
	def privmsg(self,target,msg):
		if type(target)==type(list()):
			target = ",".join(target)
		self.send("PRIVMSG "+target+" :"+msg)

	# msg()
	# Arguments: string, string
	#
	# Sends a PRIVMSG command to the IRC server
	def msg(self,target,msg):
		self.privmsg(target,msg)

	# action()
	# Arguments: string, string
	#
	# Sends a CTCP action message to the IRC server
	def action(self,target,msg):
		if type(target)==type(list()):
			target = ",".join(target)
		self.send("PRIVMSG "+target+" :\x01ACTION "+msg+"\x01")

	# me()
	# Arguments: string, string
	#
	# Sends a CTCP action message to the IRC server
	def me(self,target,msg):
		self.action(target,msg)

	# notice()
	# Arguments: string, string
	#
	# Sends a NOTICE command to the IRC server
	def notice(self,target,msg):
		if type(target)==type(list()):
			target = ",".join(target)
		self.send("NOTICE "+target+" :"+msg)

	# cnotice()
	# Arguments: string, string, string
	#
	# Sends a CNOTICE command to the IRC server
	def cnotice(self,target,channel,msg):
		if type(target)==type(list()):
			target = ",".join(target)
		self.send("CNOTICE "+target+" "+channel+" :"+msg)

	# cprivmsg()
	# Arguments: string, string, string
	#
	# Sends a CPRIVMSG command to the IRC server
	def cprivmsg(self,target,channel,msg):
		if type(target)==type(list()):
			target = ",".join(target)
		self.send("CPRIVMSG "+target+" "+channel+" :"+msg)

	# kick()
	# Arguments: string, string, string
	#
	# Sends a KICK command to the IRC server
	def kick(self,target,channel,reason=None):
		if reason:
			self.send("KICK "+channel+" "+target+" :"+reason)
		else:
			self.send("KICK "+channel+" "+target+" :")

	# invite()
	# Arguments: string, string
	#
	# Sends a INVITE command to the IRC server
	def invite(self,user,channel):
		self.send("INVITE "+user+" "+channel)

	# whois()
	# Arguments: string
	#
	# Sends a WHOIS command to the IRC server
	def whois(self,user):
		self.send("WHOIS "+user)

	# list()
	# Arguments: NONE
	#
	# Sends a LIST command to the IRC server
	def list(self):
		self.send("LIST")

	# away()
	# Arguments: string
	#
	# Sends an AWAY command to the IRC server
	def away(self,msg=None):
		if msg==None:
			self.send("AWAY")
		else:
			self.send("AWAY "+msg)

	# back()
	# Arguments: NONE
	#
	# Sends a BACK command to the IRC server
	def back(self):
		self.send("BACK")

	# ban()
	# Arguments: string, string
	#
	# Sends a ban message to the IRC server
	def ban(self,channel,mask):
		self.send("MODE "+channel+" +b "+mask)

	# unban()
	# Arguments: string, string
	#
	# Sends a unban message to the IRC server
	def unban(self,channel,mask):
		self.send("MODE "+channel+" -b "+mask)

	# lock()
	# Arguments: string, string
	#
	# Sets a channel key on a channel
	def lock(self,channel,key):
		self.send("MODE "+channel+" +k "+key)

	# unlock()
	# Arguments: string, string
	#
	# Removes a channel key from a channel
	def unlock(self,channel,key):
		self.send("MODE "+channel+" -k "+key)

	# mode()
	# Arguments: string, string
	#
	# Sets (or unsets) a mode on a channel or person
	def mode(self,target,mode):
		self.send("MODE "+target+" "+mode)


class Uptimer(threading.Thread):
	def __init__(self, event, eobj):
		threading.Thread.__init__(self)
		self.stopped = event
		self.erkle = eobj

	# Execute the Erkle object's _uptime_clock_tick() method
	def run(self):
		while not self.stopped.wait(1):
			self.erkle._uptime_clock_tick()

class Clock(threading.Thread):
	def __init__(self, event, eobj):
		threading.Thread.__init__(self)
		self.stopped = event
		self.erkle = eobj

	# Execute the Erkle object's _regular_clock_tick() method
	def run(self):
		while not self.stopped.wait(self.erkle._clock_resolution):
			self.erkle._regular_clock_tick()


class ChannelData:
	def __init__(self,name,usercount,topic):
		self.name = name
		self.users = usercount
		self.topic = topic

class UserData:
	def __init__(self,nickname,username,host,op,voiced,owner,admin,halfop):
		self.nickname = nickname
		self.username = username
		self.host = host
		self.op = op
		self.voiced = voiced
		self.owner = owner
		self.admin = admin
		self.halfop = halfop

class WhoisData:
	def __init__(self,nickname):
		self.nickname = nickname
		self.username = ""
		self.host = ""
		self.realname = ""
		self.privs = None
		self.idle = 0
		self.signon = 0
		self.channels = []
		self.server = ""

def parse_username(user):
	isop = False
	isvoiced = False
	isowner = False
	isadmin = False
	ishalfop = False

	parsed = user.split('!')
	nickname = parsed[0]
	hostmask = parsed[1]
	parsed = hostmask.split('@')
	username = parsed[0]
	host = parsed[1]

	rawnick = ''
	for c in nickname:
		if c=='@':
			isop = True
			continue
		if c=='%':
			ishalfop = True
			continue
		if c=='+':
			isvoiced = True
			continue
		if c=='~':
			isowner = True
			continue
		if c=='&':
			isadmin = True
			continue
		rawnick = rawnick + c

	return UserData(rawnick,username,host,isop,isvoiced,isowner,isadmin,ishalfop)

def clean_out_duplicate_users(ulist):
	nick = []
	cleaned = []
	for u in ulist:
		if u.nickname in nick: continue
		nick.append(u.nickname)
		cleaned.append(u)

	return cleaned


def raise_error_double_target_event(eobj,code,tokens):
	tokens.pop(0)	# remove server
	tokens.pop(0)	# reove message type
	tokens.pop(0)	# remove nick

	target = tokens.pop(0)
	target2 = tokens.pop(0)
	reason = ' '.join(tokens)
	reason = reason[1:]

	irc.call("error",eobj,code,f"{target} {target2}",reason)

def raise_error_target_event(eobj,code,tokens):
	tokens.pop(0)	# remove server
	tokens.pop(0)	# reove message type
	tokens.pop(0)	# remove nick

	target = tokens.pop(0)
	reason = ' '.join(tokens)
	reason = reason[1:]

	irc.call("error",eobj,code,target,reason)

def raise_error_event(eobj,code,line):
	parsed = line.split(':')
	if len(parsed)>=2:
		reason = parsed[1]
	else:
		reason = UNKNOWN_ERROR

	irc.call("error",eobj,code,None,reason)

def handle_errors(eobj,line):

	tokens = line.split()

	if tokens[1]=="400":
		irc.call("error",eobj,"400",None,UNKNOWN_ERROR)
		return True

	if tokens[1]=="401":
		raise_error_target_event(eobj,"401",tokens)
		return True

	if tokens[1]=="402":
		raise_error_target_event(eobj,"402",tokens)
		return True

	if tokens[1]=="403":
		raise_error_target_event(eobj,"403",tokens)
		return True

	if tokens[1]=="404":
		raise_error_target_event(eobj,"404",tokens)
		return True

	if tokens[1]=="405":
		raise_error_target_event(eobj,"405",tokens)
		return True

	if tokens[1]=="406":
		raise_error_target_event(eobj,"406",tokens)
		return True

	if tokens[1]=="407":
		raise_error_target_event(eobj,"407",tokens)
		return True

	if tokens[1]=="409":
		raise_error_event(eobj,"409",line)
		return True

	if tokens[1]=="411":
		raise_error_event(eobj,"411",line)
		return True

	if tokens[1]=="412":
		raise_error_event(eobj,"412",line)
		return True

	if tokens[1]=="413":
		raise_error_target_event(eobj,"413",tokens)
		return True

	if tokens[1]=="414":
		raise_error_target_event(eobj,"414",tokens)
		return True

	if tokens[1]=="415":
		raise_error_target_event(eobj,"415",tokens)
		return True

	if tokens[1]=="421":
		raise_error_target_event(eobj,"421",tokens)
		return True

	if tokens[1]=="422":
		raise_error_event(eobj,"422",line)
		return True

	if tokens[1]=="423":
		raise_error_target_event(eobj,"423",tokens)
		return True

	if tokens[1]=="424":
		raise_error_event(eobj,"424",line)
		return True

	if tokens[1]=="431":
		raise_error_event(eobj,"431",line)
		return True

	if tokens[1]=="432":
		raise_error_target_event(eobj,"432",tokens)
		return True

	if tokens[1]=="436":
		raise_error_target_event(eobj,"436",tokens)
		return True

	if tokens[1]=="441":
		raise_error_double_target_event(eobj,"441",tokens)
		return True

	if tokens[1]=="442":
		raise_error_target_event(eobj,"442",tokens)
		return True

	if tokens[1]=="444":
		raise_error_target_event(eobj,"444",tokens)
		return True

	if tokens[1]=="445":
		raise_error_event(eobj,"445",line)
		return True

	if tokens[1]=="446":
		raise_error_event(eobj,"446",line)
		return True

	if tokens[1]=="451":
		raise_error_event(eobj,"451",line)
		return True

	if tokens[1]=="461":
		raise_error_target_event(eobj,"461",tokens)
		return True

	if tokens[1]=="462":
		raise_error_event(eobj,"462",line)
		return True

	if tokens[1]=="463":
		raise_error_event(eobj,"463",line)
		return True

	if tokens[1]=="464":
		raise_error_event(eobj,"464",line)
		return True

	if tokens[1]=="465":
		raise_error_event(eobj,"465",line)
		return True

	if tokens[1]=="467":
		raise_error_target_event(eobj,"467",tokens)
		return True

	if tokens[1]=="471":
		raise_error_target_event(eobj,"471",tokens)
		return True

	if tokens[1]=="472":
		raise_error_target_event(eobj,"472",tokens)
		return True

	if tokens[1]=="473":
		raise_error_target_event(eobj,"473",tokens)
		return True

	if tokens[1]=="474":
		raise_error_target_event(eobj,"474",tokens)
		return True

	if tokens[1]=="475":
		raise_error_target_event(eobj,"475",tokens)
		return True

	if tokens[1]=="476":
		raise_error_target_event(eobj,"476",tokens)
		return True

	if tokens[1]=="478":
		raise_error_double_target_event(eobj,"478",tokens)
		return True

	if tokens[1]=="481":
		raise_error_event(eobj,"481",line)
		return True

	if tokens[1]=="482":
		raise_error_target_event(eobj,"482",tokens)
		return True

	if tokens[1]=="483":
		raise_error_event(eobj,"483",line)
		return True

	if tokens[1]=="485":
		raise_error_event(eobj,"481",line)
		return True

	if tokens[1]=="491":
		raise_error_event(eobj,"491",line)
		return True

	if tokens[1]=="501":
		raise_error_event(eobj,"501",line)
		return True

	if tokens[1]=="502":
		raise_error_event(eobj,"502",line)
		return True

	return False


def handle_information(eobj,line):

	tokens = line.split()
	#print(line)

	# listend
	if tokens[1]=="323":
		eobj.channels = eobj._channels
		irc.call("list",eobj,eobj._channels)
		return True

	# liststart
	if tokens[1]=="321":
		eobj._channels = []
		return True

	# list
	if tokens[1]=="322":

		tokens.pop(0)	# remove server
		tokens.pop(0)	# reove message type
		tokens.pop(0)	# remove nick

		channel = tokens.pop(0)
		usercount = tokens.pop(0)

		try:
			usercount = int(usercount)
		except:
			usercount = 0

		tokens.pop(0)	# remove colon

		if len(tokens)>0:
			topic = ' '.join(tokens)
		else:
			topic = None

		#c = [channel,usercount,topic]
		c = ChannelData(channel,usercount,topic)
		eobj._channels.append(c)
		return True

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

		irc.call("mode",eobj,nickname,host,target,mode)

		return True

	# chanmodeis
	if tokens[1]=="324":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type

		channel = tokens.pop(0)
		mode = ' '.join(tokens)
		mode = mode.replace(':','',1)

		irc.call("mode",eobj,eobj.hostname,eobj.hostname,target,mode)
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
		irc.call("topic",eobj,nickname,host,channel,topic)

		return True

	# 331 no topic
	if tokens[1]=="331":
		tokens.pop(0)	# remove server name
		tokens.pop(0)	# remove message type
		tokens.pop(0)	# remove nickname

		channel = tokens.pop(0)

		eobj.topic[channel] = ''
		irc.call("topic",eobj,eobj.hostname,eobj.hostname,channel,None)
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
			irc.call("topic",eobj,eobj.hostname,eobj.hostname,channel,topic)
		else:
			eobj.topic[channel] = ''
			irc.call("topic",eobj,eobj.hostname,eobj.hostname,channel,None)
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
		irc.call("motd",eobj,motd)
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
			del eobj.users[channel]
			del eobj.topic[channel]
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
			del eobj.users[channel]
			del eobj.topic[channel]
			irc.call("parted",eobj,channel)
			return

		irc.call("part",eobj,nickname,host,channel,reason)

		cleaned = []
		for u in eobj.users[channel]:
			if u.nickname==nickname: continue
			cleaned.append(cuser)
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
