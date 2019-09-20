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

from erkle import *

import erkle.events.dump

import sys

print("Example bot for Erkle "+ERKLE_VERSION)

@irc.event("private")
def fevent(connection,nickname,host,message):
	if message.lower().strip()=="list":
		connection.list()

@irc.event("private")
def fevent(connection,nickname,host,message):
	if message.lower().strip()=="quit":
		connection.quit()
		sys.exit()

@irc.event("private","quiet")
def fevent(connection,nickname,host,message):
	if message.lower().strip()=="quiet":
		c.disable("erkle.events.dump")

@irc.event("private","quiet")
def fevent(connection,nickname,host,message):
	if message.lower().strip()=="loud":
		c.enable("erkle.events.dump")

@irc.event("registered")
def fevent(connection):
	print("Registered!")
	connection.join("#erklelib")

c = Erkle("erklebot","localhost",port=6667,username="erklebot",realname='erkle bot',alternate='erk1eb0t',
			password=None,ssl=False,encoding='utf-8',flood_protection=True,flood_rate=2,clock_frequency=1.0,
			multithread=False,debug_input=False,debug_output=False,daemon=False,socket=None)

c.connect()
