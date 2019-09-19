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

import threading

#--SINGLE_FILE--#

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

#--SINGLE_FILE--#