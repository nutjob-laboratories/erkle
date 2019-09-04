<p align="center">
	<img src="https://github.com/nutjob-laboratories/erkle/raw/master/images/logo_300x100.png">
</p>

An easy to use, event-driven, low-level IRC library for Python 3. It is being written as a replacement for Twisted in the [Erk IRC Client](https://github.com/nutjob-laboratories/erk).

# Example
```python
from erkle import *

@hook.event("welcome")
def welcome(connection):
	connection.join("#erklelib")

@hook.event("join")
def cjoin(connection,nickname,host,channel):
	if nickname == connection.nickname:
		connection.msg("Hello everyone!")
	else:
		connection.msg(f"Hello, {nickname}! Welcome to {channel}!")

client = ErkleClient("erklebot","bot","Erkle Example Bot","irc.efnet.org")
client.connect()
```

# Another IRC library? Why not use Twisted/irclib/...?
Honestly? Because I got sick of working around Twisted's foibles, and didn't really want to learn _another_ IRC library. **Erkle** uses Python's built-in library only, with the exception of the `ssl` library (which requires [pyOpenSSL](https://www.pyopenssl.org/)), and is only necessary if you want to use SSL to connect to IRC servers.

There's no subclassing, inheritance, or anything else needed to use **Erkle**. Just write some functions, hook them to IRC events, and you're done.

# Documentation
**Erkle**'s documentation is available [here](https://github.com/nutjob-laboratories/erkle/blob/master/documentation/erkle.pdf).
