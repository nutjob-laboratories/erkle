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

SSL_AVAILABLE = True
try:
	import ssl
except ImportError:
	SSL_AVAILABLE = False

from erkle.hooks import hook
from erkle.information import handle_information
from erkle.users import handle_users
from erkle.errors import handle_errors

class Erkle:

	# __init__()
	# Arguments: string, string, string, string, integer, string, boolean, string
	#
	# Initializes an Erkle() object.
	def __init__(self,nickname,username,realname,server,port=6667,password=None,usessl=False,encoding="utf-8"):
		self.nickname = nickname
		self.username = username
		self.realname = realname
		self.server = server
		self.port = port
		self.password = password
		self.usessl = usessl
		self.encoding = encoding

		self.connected = False
		self.current_nickname = nickname

		# If SSL isn't available, set self.usessl to false
		if not SSL_AVAILABLE:
			self.usessl = False

		self._buffer = ""				# Where incoming server data is stored
		self._channels = []				# Channel list buffer
		self._thread = None				# If spawn()ed, stores the object's thread

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
		self.whois = {}					# WHOIS data buffer

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
		#hook.add(self,t)
		self._thread = t
		t.start()

	# _run()
	# Arguments: none
	#
	# Connects to IRC and starts the loop that receives messages from the server
	# and handles them.
	def _run(self):

		# Raise the "start" event
		hook.call("start",self)

		# Create the connection socket and connect to the server
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.connection.connect((self.server,self.port))

		## SSL-ify the connection if needed
		if self.usessl:
			self.connection = ssl.wrap_socket(self.connection)

		# Raise the "connect" event
		hook.call("connect",self)

		# Get the server to send nicks/hostmasks
		self.send("PROTOCTL UHNAMES")

		# Send server password, if necessary
		if self.password:
			self.send(f"PASS {self.password}")

		# Send user information
		self.send(f"NICK {self.nickname}")
		self.send(f"USER {self.username} 0 0 :{self.realname}")

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
				hook.call("line",self,line)

				# Handle the line
				self.handle(line)

	# handle()
	# Arguments: string
	#
	# Parses IRC messages from the server, and triggers events
	def handle(self,line):

		tokens = line.split()

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
			self.connected = True
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

		# Error management
		if handle_errors(self,line): return

		# Server options
		if handle_information(self,line): return

		# User management
		if handle_users(self,line): return

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
		if self._thread != None: sys.exit()

	# send()
	# Arguments: string
	#
	# Sends a message to the IRC server
	def send(self,data):
		self.connection.send(bytes(data + "\r\n", "utf-8"))

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
		self.connection.shutdown(socket.SHUT_RDWR)
		self.connection.close()

		# Exit the thread, if we're running in a thread
		if self._thread != None: sys.exit()

	# privmsg()
	# Arguments: string, string
	#
	# Sends a PRIVMSG command to the IRC server
	def privmsg(self,target,msg):
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
		self.send("NOTICE "+target+" "+msg)

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
