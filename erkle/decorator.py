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

from erkle.common import *

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


