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
from erkle import *

import erkle.events.dump

PARTYLINE_USERS,USED_PORTS = [],[]

# Offer a DCC chat connection to anyone who
# sends "partyline" as a private message
@irc.event("private")
def fevent(connection,nickname,host,message):
	if message.lower().strip()=="partyline":

		# Select a random port number from
		# 10,000 to 60,000
		rport = random.randint(10000,60000)
		while rport in USED_PORTS:
			rport = random.randint(10000,60000)
		USED_PORTS.append(rport)

		# Connect user to DCC chat
		connection.dccchat(nickname,rport,"127.0.0.1")

# A user has connected to the partyline
@irc.event("dcc-chat-accept")
def fevent(connection,nickname,address,port,clientid):
	# Add the user to the list of partyline users
	if not clientid in PARTYLINE_USERS:
		PARTYLINE_USERS.append(clientid)

	# Welcome the new user to the partyline
	connection.chat(clientid,"Welcome to the erklebot partyline!")

	# Notify everyone that the user has joined the partyline
	broadcast(connection,clientid,nickname+" has joined the partyline.")

# A user has disconnected from the partyline
@irc.event("dcc-chat-end")
def fevent(connection,nickname,address,port,clientid):
	# Remove the user from the list of partyline users
	try:
		PARTYLINE_USERS.remove(clientid)
	except:
		pass

	# Notify everyone else that the user left the partyline
	broadcast(connection,0,nickname+" has left the partyline.")

# A user sent a DCC chat message to the partyline
@irc.event("dcc-chat")
def fevent(connection,nickname,clientid,message):
	# Format chat for broadcast
	outmsg = "<"+nickname+"> "+message

	# Broadcast the chat to all clients except
	# the user who sent the chat
	broadcast(connection,clientid,outmsg)

# Join the #erklelib channel on connection to IRC
@irc.event("registered")
def fevent(connection):
	connection.join("#erklelib")

# broadcast()
# Sends DCC chat messages to all users except
# for one (the user who sent out the DCC chat
# message. Set "clientid" to 0 (zero) to send
# to all users in the partyline.
def broadcast(connection,clientid,message):
	for user in PARTYLINE_USERS:
		if user != clientid:
			connection.chat(user,message)

# Create the Erkle object and connect to IRC
c = Erkle("erkleparty","localhost")
c.connect()
