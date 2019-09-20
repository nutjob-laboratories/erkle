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

from erkle.decorator import irc
from erkle.information import handle_information
from erkle.users import handle_users
from erkle.errors import handle_errors
from erkle.clock import Uptimer,Clock
from erkle.common import *

#--SINGLE_FILE--#

class Erkle:

	# __init__()
	# Arguments: dict
	#
	# Initializes an Erkle() object.
	# def __init__(self,serverinfo):
	def __init__(self,nickname,server,**kwargs):

		self.nickname = nickname
		self.server = server

		self.port = 6667
		self.username = None
		self.alternate = None
		self.password = None
		self.usessl = False
		self.realname = DEFAULT_REALNAME
		self.encoding = "utf-8"
		self.flood_protection = True
		self.floodrate = 2
		self._clock_resolution = 1.0
		self._multithreaded = False
		self._show_input = False
		self._show_output = False
		self._daemon = False

		for key, value in kwargs.items():

			if key=="socket":
				if value!=None:
					global socket
					socket = value

			if key=='daemon':
				self._daemon = value

			if key=='debug_output':
				self._show_output = value

			if key=='debug_input':
				self._show_input = value

			if key=='multithread':
				self._multithreaded = value

			if key=='clock_frequency':
				self._clock_resolution = value

			if key=='flood_protection':
				self.flood_protection = value

			if key=='flood_rate':
				self.floodrate = value

			if key=='username':
				self.username = value

			if key=='realname':
				self.realname = value

			if key=='alternate':
				self.alternate = value

			if key=='port':
				self.port = value

			if key=='password':
				self.password = value

			if key=='ssl':
				self.usessl = value

			if key=='encoding':
				self.encoding = value

		if self.alternate==None: self.alternate = self.nickname + "_"
		if self.username==None: self.username = self.nickname

		# Create the socket
		self._client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		# Check to make sure all config input is the right variable type
		self._check_configuration_input_type('nickname',self.nickname,str())
		self._check_configuration_input_type('username',self.username,str())
		self._check_configuration_input_type('realname',self.realname,str())
		self._check_configuration_input_type('alternate',self.alternate,str())
		self._check_configuration_input_type('server',self.server,str())
		self._check_configuration_input_type('port',self.port,int())
		self._check_configuration_input_type('ssl',self.usessl,bool())
		self._check_configuration_input_type('encoding',self.encoding,str())
		self._check_configuration_input_type('flood_protection',self.flood_protection,bool())
		self._check_configuration_input_type('multithreaded',self._multithreaded,bool())
		self._check_configuration_input_type('debug_input',self._show_input,bool())
		self._check_configuration_input_type('debug_output',self._show_output,bool())
		self._check_configuration_input_type('daemon',self._daemon,bool())

		# Make sure flood_rate is an int or a float
		if type(self.floodrate)!=type(int()):
			if type(self.floodrate)!=type(float()):
				print("ERROR: "+WRONG_VARIABLE_TYPE.format(key='flood_rate',rec=intype,exp='int'))
				sys.exit(1)

		# Make sure clock_frequency is a in for a float
		if type(self._clock_resolution)!=type(int()):
			if type(self._clock_resolution)!=type(float()):
				print("ERROR: "+WRONG_VARIABLE_TYPE.format(key='clock_frequency',rec=intype,exp='float'))
				sys.exit(1)


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
		# self._client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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

				if self._show_input: print("<- "+line)

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

		if self._show_output: print("-> "+data)

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
			if self._daemon: t.daemon = True
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
	# Arguments: none *or* socket-a-like object
	#
	# Returns the object's socket
	def socket(self,sobj=None):
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

#--SINGLE_FILE--#