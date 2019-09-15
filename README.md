<p align="center">
	<img src="https://github.com/nutjob-laboratories/erkle/raw/master/images/logo_300.png"><br>
	<a href="https://github.com/nutjob-laboratories/erkle/blob/master/documentation/Erkle-IRC-Library.pdf"><b>Documentation for Erkle 0.035</b></a><br>
	<a href="https://github.com/nutjob-laboratories/erkle/raw/master/downloads/erkle-irclib.zip"><b>Download the Erkle IRC Library for Python 3</b></a>
</p>

An easy to use, event-driven, low-level IRC library for Python 3. It is being written as a replacement for Twisted in the [Erk IRC Client](https://github.com/nutjob-laboratories/erk). The current version of **Erkle** is 0.035.

**Erkle** is not feature complete, but it is complete enough for most simple IRC bots.

# Features

* Small (less than 150KB!) and easy to bundle with applications
* Fast
* Multiple connection/client support
* SSL/TLS connection support
* Flood protection
* Built-in localzation (supported languages: English, French, and German)

# Requirements

* [sys](https://docs.python.org/3/library/sys.html)
* [os](https://docs.python.org/3/library/os.html)
* [socket](https://docs.python.org/3/library/socket.html)
* [collections](https://docs.python.org/3/library/collections.html)
* [string](https://docs.python.org/3/library/string.html)
* [threading](https://docs.python.org/3/library/threading.html)
* [importlib](https://docs.python.org/3/library/importlib.html)
* [ssl](https://docs.python.org/3/library/ssl.html) (optional)

**Erkle** uses, with one exception, only modules from the standary Python library. The `ssl` library is only necessary if you want to connected to an IRC server via SSL/TLS. To use the `ssl` module, the OpenSSL library must be installed. The easiest way to install this library is to use `pip` to install the pyOpenSSL library:

```
pip install pyopenssl
```

# Example
```python
from erkle import *

@irc.event("registered")
def welcome(connection):
	connection.join("#erklelib")

@irc.event("join")
def cjoin(connection,nickname,host,channel):
	if nickname == connection.nickname:
		connection.msg("Hello everyone! I'm here!")
	else:
		connection.msg(f"Hello, {nickname}! Welcome to {channel}!")

configuration = {
	'nickname': 'erklebot',
	'username': 'erkle',
	'realname': 'Erkle Example Bot',
	'alternate': 'erk1eb0t',
	'server':'irc.efnet.org',
	'encoding': 'UTF-8'
}

client = Erkle(configuration)
client.connect()
```

# Another IRC library? Why not use Twisted/irclib/...?
Honestly? Because I got sick of working around Twisted's foibles, and didn't really want to learn _another_ IRC library. **Erkle** uses Python's built-in library only, with the exception of the `ssl` library (which requires [pyOpenSSL](https://www.pyopenssl.org/)), and is only necessary if you want to use SSL to connect to IRC servers.

There's no subclassing, inheritance, or anything else needed to use **Erkle**. Just write some functions, hook them to IRC events, and you're done.

# Documentation
**Erkle**'s documentation is available [here](https://github.com/nutjob-laboratories/erkle/blob/master/documentation/Erkle-IRC-Library.pdf).
