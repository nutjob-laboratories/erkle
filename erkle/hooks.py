
class HookHandler:
	def __init__(self):
		self._handlers = {}

	def call(self,type,*args):
		if type in self._handlers:
			for h in self._handlers[type]:
				h(*args)

	def event(self, type):
		def registerhandler(handler):
			if type in self._handlers:
				self._handlers[type].append(handler)
			else:
				self._handlers[type] = [handler]
			return handler
		return registerhandler

hook = HookHandler()
