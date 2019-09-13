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
import importlib

SSL_AVAILABLE = True
try:
	import ssl
except ImportError:
	SSL_AVAILABLE = False

from erkle.decorator import irc
from erkle.information import handle_information
from erkle.users import handle_users
from erkle.errors import handle_errors
from erkle.clock import Uptimer
from erkle.common import *
# from erkle.strings import *

class Erkle:

	# __init__()
	# Arguments: dict
	#
	# Initializes an Erkle() object.
	def __init__(self,serverinfo):

		self.language = "en"
		if 'language' in serverinfo:
			self.language = serverinfo['language']

		self._load_localization_strings(self.language)

		self.nickname = None
		if 'nickname' in serverinfo:
			self.nickname = serverinfo['nickname']
		if 'nick' in serverinfo:
			self.nickname = serverinfo['nick']
		if self.nickname == None:
			self._display_error_and_exit(NO_NICKNAME_IN_DICT_ERROR)

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

		if 'server' in serverinfo:
			self.server = serverinfo['server']
		else:
			self._display_error_and_exit(NO_SERVER_IN_DICT_ERROR)

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

		if 'flood' in serverinfo:
			if serverinfo['flood']:
				self.flood_protection = False
			else:
				self.flood_protection = True
		else:
			self.flood_protection = True

		if 'floodrate' in serverinfo:
			self.floodrate = serverinfo['floodrate']
		else:
			self.floodrate = 2

		self._started = False
		self.current_nickname = self.nickname

		# If SSL isn't available, and SSL is set to
		# be used, raise an error
		if not SSL_AVAILABLE:
			if self.usessl:
				self._display_error_and_exit(NO_SSL_ERROR)

		self._buffer = ""				# Incoming data buffer
		self._channels = []				# Channel list buffer
		self._thread = None				# If spawn()ed, stores the object's thread
		self._whois = {}				# WHOIS data buffer
		self._message_queue = []		# Outgoing message queue for flood protection
		self._last_message_time = 0		# The time the last message was sent to the server

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
		self.channels = []				# Server channel list

		self.tags = []					# Object tags
		self.uptime = 0					# Object uptime, in seconds

	# _run()
	# Arguments: none
	#
	# Connects to IRC and starts the loop that receives messages from the server
	# and handles them.
	def _run(self):

		self.stoptimer = threading.Event()
		self.uptimer = Uptimer(self.stoptimer,self)
		self.uptimer.start()

		# Set object state as "started"
		self._started = True

		# Raise the "start" event
		irc.call("connecting",self)

		# Create the connection socket and connect to the server
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.connection.connect((self.server,self.port))

		## SSL-ify the connection if needed
		if self.usessl:
			self.connection = ssl.wrap_socket(self.connection)

		# Raise the "connect" event
		irc.call("connect",self)

		# Get the server to send nicks/hostmasks
		self._send("PROTOCTL UHNAMES")

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
				line = self.connection.recv(4096)

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

				# Stop the timer
				self.stoptimer.set()

				# Shutdown the connection
				self.connection.shutdown(socket.SHUT_RDWR)
				self.connection.close()
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
			if self.current_nickname==self.nickname:
				# Use alternate nick
				if self.nickname == self.alternate:
					self.nickname = self.nickname + "_"
					self.current_nickname = self.nickname
					self._send(f"NICK {self.nickname}")
				else:
					self.nickname = self.alternate
					self.current_nickname = self.alternate
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

	# _uptime_clock_tick()
	# Arguments: none
	#
	# Increments the uptime by one second, and calls
	# _sendqueue() to send queued messages.
	def _uptime_clock_tick(self):
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

	# _load_localization_strings()
	# Arguments: string
	#
	# Loads the localized string module for application messages.
	def _load_localization_strings(self,lang):
		# https://stackoverflow.com/questions/21221358/python-how-to-import-all-methods-and-attributes-from-a-module-dynamically

		# Load in the language's strings module
		lang_module = importlib.import_module('erkle.localization.'+lang+'.strings')

		# Import all variables/etc from the strings module
		module_dict = lang_module.__dict__
		try:
			to_import = lang_module.__all__
		except AttributeError:
			to_import = [name for name in module_dict if not name.startswith('_')]
		globals().update({name: module_dict[name] for name in to_import})


	# _display_error_and_exit()
	# Arguments: string
	#
	# Displays an error message and exits
	def _display_error_and_exit(self,msg):
		print(ERROR_WORD+": "+msg)
		sys.exit(1)

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

	# send()
	# Arguments: string
	#
	# Sends a message to the IRC server
	def _send(self,data):
		#self.connection.send(bytes(data + "\r\n", "utf-8"))

		sender = getattr(self.connection, 'write', self.connection.send)
		try:
			sender(bytes(data + "\r\n", "utf-8"))
		except socket.error:
			print(SEND_MESSAGE_ERROR)

			# Shutdown the connection and exit
			self.connection.shutdown(socket.SHUT_RDWR)
			self.connection.close()
			sys.exit(1)

	# tag()
	# Arguments: string[, string,...]
	#
	# Adds a tag to the Erkle object
	def tag(self,*args):
		for t in args:
			self.tags.append(t)
			irc._disabled = list(dict.fromkeys(irc._disabled))

	# untag()
	# Arguments: string[, string,...]
	#
	# Removes a tag from the Erkle object
	def untag(self,*args):
		for t in args:
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
		self._run()

	# spawn()
	# Arguments: none
	#
	# Calls _run() and runs it in a separate thread.
	def spawn(self):
		t = threading.Thread(name=f"{self.server}:{str(self.port)}",target=self._run)
		self._thread = t
		t.start()

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
		# Stop the timer
		self.stoptimer.set()

		if self._thread != None: sys.exit()

	# send()
	# Arguments: string
	#
	# If flood protection is turned on, adds a message
	# to the outgoing message queue. If flood protection
	# is turned off, directly sends a message to
	# the IRC server.
	def send(self,data):

		if self._not_started():
			print(f"Can't send message \"{data}\"")
			sys.exit()

		if self.flood_protection:
			if (self._last_message_time + self.floodrate) <= self.uptime:
				self._last_message_time = self.uptime
				self._send(data)
			else:
				self._message_queue.append(data)
		else:
			self._send(data)

	# join()
	# Arguments: string, string
	#
	# Sends a JOIN command to the IRC server
	def join(self,channel,key=None):
		if key:
			# self.send("JOIN "+channel+" "+key)
			self.send("JOIN "+channel+" "+key)
		else:
			# self.send("JOIN "+channel)
			self.send("JOIN "+channel)

	# part()
	# Arguments: string, string
	#
	# Sends a PART command to the IRC server
	def part(self,channel,reason=None):
		if reason:
			# self.send("PART "+channel+" "+reason)
			self.send("PART "+channel+" "+reason)
		else:
			# self.send("PART "+channel)
			self.send("PART "+channel)

	# quit()
	# Arguments: string
	#
	# Sends a QUIT command to the IRC server
	def quit(self,reason=''):
		if reason=='':
			# self.send("QUIT")
			self.send("QUIT")
		else:
			# self.send("QUIT "+reason)
			self.send("QUIT "+reason)
		self.connection.shutdown(socket.SHUT_RDWR)
		self.connection.close()

		# Stop the timer
		self.stoptimer.set()

		# Exit the thread, if we're running in a thread
		if self._thread != None: sys.exit()

	# privmsg()
	# Arguments: string, string
	#
	# Sends a PRIVMSG command to the IRC server
	def privmsg(self,target,msg):
		# self.send("PRIVMSG "+target+" "+msg)
		self.send("PRIVMSG "+target+" "+msg)

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
		# self.send("PRIVMSG "+target+" \x01ACTION "+msg+"\x01")
		self.send("PRIVMSG "+target+" \x01ACTION "+msg+"\x01")

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
		# self.send("NOTICE "+target+" "+msg)
		self.send("NOTICE "+target+" "+msg)

	# kick()
	# Arguments: string, string, string
	#
	# Sends a KICK command to the IRC server
	def kick(self,target,channel,reason=None):
		if reason:
			# self.send("KICK "+channel+" "+target+" :"+reason)
			self.send("KICK "+channel+" "+target+" :"+reason)
		else:
			# self.send("KICK "+channel+" "+target+" :")
			self.send("KICK "+channel+" "+target+" :")

	# invite()
	# Arguments: string, string
	#
	# Sends a INVITE command to the IRC server
	def invite(self,user,channel):
		# self.send("INVITE "+user+" "+channel)
		self.send("INVITE "+user+" "+channel)

	# whois()
	# Arguments: string
	#
	# Sends a WHOIS command to the IRC server
	def whois(self,user):
		# self.send("WHOIS "+user)
		self.send("WHOIS "+user)

	# list()
	# Arguments: NONE
	#
	# Sends a LIST command to the IRC server
	def list(self):
		# self.send("LIST")
		self.send("LIST")

	# away()
	# Arguments: string
	#
	# Sends an AWAY command to the IRC server
	def away(self,msg=None):
		if msg==None:
			# self.send("AWAY")
			self.send("AWAY")
		else:
			# self.send("AWAY "+msg)
			self.send("AWAY "+msg)

	# back()
	# Arguments: NONE
	#
	# Sends a BACK command to the IRC server
	def back(self):
		# self.send("BACK")
		self.send("BACK")

	# ban()
	# Arguments: string, string
	#
	# Sends a ban message to the IRC server
	def ban(self,channel,mask):
		# self.send("MODE "+channel+" +b "+mask)
		self.send("MODE "+channel+" +b "+mask)

	# unban()
	# Arguments: string, string
	#
	# Sends a unban message to the IRC server
	def unban(self,channel,mask):
		# self.send("MODE "+channel+" -b "+mask)
		self.send("MODE "+channel+" -b "+mask)

	# lock()
	# Arguments: string, string
	#
	# Sets a channel key on a channel
	def lock(self,channel,key):
		# self.send("MODE "+channel+" +k "+key)
		self.send("MODE "+channel+" +k "+key)

	# unlock()
	# Arguments: string, string
	#
	# Removes a channel key from a channel
	def unlock(self,channel,key):
		# self.send("MODE "+channel+" -k "+key)
		self.send("MODE "+channel+" -k "+key)

	# mode()
	# Arguments: string, string
	#
	# Sets (or unsets) a mode on a channel or person
	def mode(self,target,mode):
		# self.send("MODE "+target+" "+mode)
		self.send("MODE "+target+" "+mode)
