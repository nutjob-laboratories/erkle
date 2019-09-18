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

class User:
	def __init__(self,nickname,username,host,op,voiced,owner,admin,halfop):
		self.nickname = nickname
		self.username = username
		self.host = host
		self.op = op
		self.voiced = voiced
		self.owner = owner
		self.admin = admin
		self.halfop = halfop

class Whois:
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

	return User(rawnick,username,host,isop,isvoiced,isowner,isadmin,ishalfop)

def clean_out_duplicate_users(ulist):
	nick = []
	cleaned = []
	for u in ulist:
		if u.nickname in nick: continue
		nick.append(u.nickname)
		cleaned.append(u)

	return cleaned
