# partyline.py
#
# A DCC partyline IRC bot written with Erkle
#
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

import random
import argparse
import sys

from erkle import *

# Partyline command names
PARTYLINE_COMMAND_TRIGGER	= "partyline"
HELP_COMMAND_TRIGGER		= "help"
LIST_COMMAND_TRIGGER		= "list"
JOIN_COMMAND_TRIGGER		= "join"
QUIT_COMMAND_TRIGGER		= "quit"

# Process command-line arguments
parser = argparse.ArgumentParser(
	prog=f"python partyline.py",
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=f"""
A partyline bot for IRC

Copyright (C) 2019  Dan Hetrick
""")

parser.add_argument('clserver', metavar='SERVER', type=str, nargs='?', help='Server to connect to on startup', default="")
parser.add_argument('clport', metavar='PORT', type=int, nargs='?', help='Port (6667)', default=6667)
parser.add_argument("--minimum", type=int,help="Lowest assigned port number (10000)",default=10000)
parser.add_argument("--maximum", type=int,help="Highest assigned port number (60000)",default=60000)
parser.add_argument("--name", type=str,help="The partyline's displayed name (\"Partyline\")",default="Partyline")
parser.add_argument("-n","--nickname", type=str,help="The nickname to use (\"erkleparty\")",default="erkleparty")
parser.add_argument( "-v","--verbose", help=f"Verbose mode", action="store_true")
parser.add_argument("--default", type=str,help="The partyline's default channel (\"#lobby\")",default="#lobby")
parser.add_argument('-c','--channel', action='append', help="Add a channel to join")
parser.add_argument("--command", type=str,help="Partyline command prefix",default=".")

args = parser.parse_args()

if len(args.clserver)==0:
	print("No server!")
	sys.exit(1)
else:
	IRC_SERVER = args.clserver

if args.verbose:
	import erkle.events.dump

PARTYLINE_COMMAND_TRIGGER	= args.command+PARTYLINE_COMMAND_TRIGGER
HELP_COMMAND_TRIGGER		= args.command+HELP_COMMAND_TRIGGER
LIST_COMMAND_TRIGGER		= args.command+LIST_COMMAND_TRIGGER
JOIN_COMMAND_TRIGGER		= args.command+JOIN_COMMAND_TRIGGER
QUIT_COMMAND_TRIGGER		= args.command+QUIT_COMMAND_TRIGGER

DEFAULT_PARTYLINE_CHANNEL = args.default

IRC_PORT = args.clport

PORT_NUMBER_MINIMUM = args.minimum
PORT_NUMBER_MAXIMUM = args.maximum

PARTYLINE_NAME = args.name

BOT_NICKNAME = args.nickname

if args.channel:
	CHANNELS_TO_JOIN = args.channel
else:
	CHANNELS_TO_JOIN = args.channel = []

# =============
# | VARIABLES |
# =============

# User information storage
PARTYLINE_USERS,USED_PORTS = [],[]

# =========================
# | ERKLE EVENT FUNCTIONS |
# =========================

# Offer a DCC chat connection to anyone who
# sends "partyline" as a private message
@irc.event("private")
def fevent(connection,nickname,host,message):
	if message.lower().strip()==PARTYLINE_COMMAND_TRIGGER.lower():

		# Generate a random port number
		rport = generate_port()
		USED_PORTS.append( PortInfo(nickname,rport) )

		# Connect user to DCC chat
		connection.dccchat(nickname,rport,connection.external_ip)

# A user has connected to the partyline
@irc.event("dcc-chat-accept")
def fevent(connection,nickname,address,port,clientid):
	# Add the user to the list of partyline users
	u = LineUser(nickname,address,port,clientid,DEFAULT_PARTYLINE_CHANNEL)
	PARTYLINE_USERS.append(u)

	# Welcome the new user to the partyline
	connection.chat(clientid,"Welcome to "+PARTYLINE_NAME+"!")
	connection.chat(clientid,"You have joined "+DEFAULT_PARTYLINE_CHANNEL)

	# Notify everyone that the user has joined the partyline
	broadcast(connection,clientid,DEFAULT_PARTYLINE_CHANNEL,nickname+" has connected to the partyline")

# A user has disconnected from the partyline
@irc.event("dcc-chat-end")
def fevent(connection,nickname,address,port,clientid):
	channel = get_channel(clientid)

	clean_user_lists(nickname,clientid)

	# Notify everyone else that the user left the partyline
	broadcast(connection,0,channel,nickname+" has disconnected from the partyline")

# A user sent a DCC chat message to the partyline
@irc.event("dcc-chat")
def fevent(connection,nickname,clientid,message):

	# Handle incoming bot commands
	tokens = message.split(' ')

	# Quit command
	# Disconnects from the partyline
	if len(tokens)==1:
		if tokens[0].lower()==QUIT_COMMAND_TRIGGER.lower():
			# Disconnect from the user
			connection.closechat(clientid)

			# Get the channel the quitting user is in
			channel = get_channel(clientid)

			# Remove user from user lists
			clean_user_lists(nickname,clientid)

			# Notify everyone else that the user left the partyline
			broadcast(connection,0,channel,nickname+" has disconnected from the partyline")
			return

	# Help command
	# Lists all available commands
	if len(tokens)==1:
		if tokens[0].lower()==HELP_COMMAND_TRIGGER.lower():
			connection.chat(clientid,PARTYLINE_NAME+" Commands")
			connection.chat(clientid,LIST_COMMAND_TRIGGER+" - Lists all users connected")
			connection.chat(clientid,QUIT_COMMAND_TRIGGER+" - Disconnects from the partyline")
			connection.chat(clientid,JOIN_COMMAND_TRIGGER+" CHANNEL - Joins a new channel")
			connection.chat(clientid,"Users can only be in one channel at a time.")
			return

	# List command
	# Compiles and sends a list of connected users
	if len(tokens)==1:
		if tokens[0].lower()==LIST_COMMAND_TRIGGER.lower():

			# Build the user list to display
			ulist = []
			for u in PARTYLINE_USERS:
				line = u.nickname+" ("+u.address+":"+str(u.port)+") is in channel "+u.channel
				ulist.append(line)
			unum = len(ulist)
			if unum==1:
				connection.chat(clientid,"There is 1 user online")
			else:
				connection.chat(clientid,"There are "+str(unum)+" users online")

			# Send the built user list
			for l in ulist:
				connection.chat(clientid,l)
			return

	# Join command
	# Joins a new channel (users can only be in one channel at
	# a time, so joining a new channel causes them to leave the
	# old channel)
	if len(tokens)==2:
		if tokens[0].lower()==JOIN_COMMAND_TRIGGER.lower():
			new_channel = tokens[1]
			for u in PARTYLINE_USERS:
				if u.id == clientid:
					old_channel = u.channel
					u.channel = new_channel
					broadcast(connection,clientid,new_channel,nickname+" has joined "+new_channel)
					broadcast(connection,clientid,old_channel,nickname+" has left "+old_channel)
					break
			return

	# Handle incoming chat

	# Format chat for broadcast
	outmsg = "<"+nickname+"> "+message
	channel = get_channel(clientid)

	# Broadcast the chat to all clients except
	# the user who sent the chat
	broadcast(connection,clientid,channel,outmsg)

# Join the #erklelib channel on connection to IRC
@irc.event("registered")
def fevent(connection):
	for channel in CHANNELS_TO_JOIN:
		connection.join(channel)

# =====================
# | SUPPORT FUNCTIONS |
# =====================

# broadcast()
# Sends DCC chat messages to all users except
# for one (the user who sent out the DCC chat
# message. Set "clientid" to 0 (zero) to send
# to all users in the partyline.
def broadcast(connection,clientid,channel,message):
	for user in PARTYLINE_USERS:
		if user.id != clientid:
			if user.channel == channel:
				connection.chat(user.id,message)

# get_channel()
# Searches the user list and returns what channel
# a particular user is in
def get_channel(clientid):
	for user in PARTYLINE_USERS:
		if user.id == clientid: return user.channel
	return DEFAULT_PARTYLINE_CHANNEL

# generate_port()
# Generates an unused port number
def generate_port():
	while True:
		used = False
		rport = random.randint(PORT_NUMBER_MINIMUM,PORT_NUMBER_MAXIMUM)
		for p in USED_PORTS:
			if p.port == rport: used = True
		if used:
			continue
		else:
			return rport

# clean_user_lists()
# Removes user from all user lists
def clean_user_lists(nickname,clientid):
	# Remove the user from the list of partyline users
	global PARTYLINE_USERS
	cleaned = []
	for u in PARTYLINE_USERS:
		if u.id == clientid: continue
		cleaned.append(u)
	PARTYLINE_USERS = cleaned

	# Remove port from list
	global USED_PORTS
	cleaned = []
	for u in USED_PORTS:
		if u.nickname==nickname: continue
		cleaned.append(u)
	USED_PORTS = cleaned

	# Clean up the port list
	if len(PARTYLINE_USERS)!=len(USED_PORTS):
		cleaned = []
		for p in USED_PORTS:
			for u in PARTYLINE_USERS:
				if u.nickname == p.nickname:
					cleaned.append(p)
		USED_PORTS = cleaned

# ===================
# | SUPPORT CLASSES |
# ===================

# LineUser
# Used to store information about connected users
class LineUser:
	def __init__(self,nickname,address,port,clientid,channel):
		self.address = address
		self.port = port
		self.nickname = nickname
		self.id = clientid
		self.channel = channel

# PortInfo
# Used to store information about port numbers in use
class PortInfo:
	def __init__(self,nickname,port):
		self.nickname = nickname
		self.port = port

# ================
# | MAIN PROGRAM |
# ================

if __name__ == "__main__":

	# Create the Erkle object and connect to IRC
	c = Erkle(BOT_NICKNAME,IRC_SERVER,port=IRC_PORT)
	c.connect()
