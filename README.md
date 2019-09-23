<p align="center">
	<img src="https://github.com/nutjob-laboratories/erkle/raw/master/images/logo_300.png"><br>
	<a href="https://github.com/nutjob-laboratories/erkle/raw/master/downloads/erkle-irclib.zip"><b>Download Erkle 0.0612</b></a><br>
	<a href="https://github.com/nutjob-laboratories/erkle/raw/master/erklelib.py"><b>Download single file Erkle 0.0612</b></a><br>
	<a href="https://github.com/nutjob-laboratories/erkle/blob/master/documentation/Erkle-IRC-Library.pdf"><b>Documentation for Erkle 0.0612</b></a><br>
</p>

**Erkle** is an open source IRC library for Python 3. It is being written as a replacement for Twisted in the [Erk IRC Client](https://github.com/nutjob-laboratories/erk). The current version of **Erkle** is 0.0612.

**Erkle** is not feature complete, but is functional for most purposes.

# Features

* (Almost) no requirements
* Open source ([MIT license](https://opensource.org/licenses/MIT))
* Small (less than 150KB, or less than 50KB for the single file version!)
* Easy to bundle with applications
* Multiple connection/client support
* SSL/TLS connection support
* Flood protection
* [Event-driven](https://en.wikipedia.org/wiki/Event-driven_programming)
* Optional multithreading
* Extremely configurable

# Requirements

* [sys](https://docs.python.org/3/library/sys.html)
* [os](https://docs.python.org/3/library/os.html)
* [socket](https://docs.python.org/3/library/socket.html)
* [collections](https://docs.python.org/3/library/collections.html)
* [string](https://docs.python.org/3/library/string.html)
* [threading](https://docs.python.org/3/library/threading.html)
* [ssl](https://docs.python.org/3/library/ssl.html) (optional)

**Erkle** uses, with one exception, only modules from the standary Python library. The [`ssl`](https://docs.python.org/3/library/ssl.html) library is only necessary if you want to connected to an IRC server via SSL/TLS. To use the `ssl` module, the OpenSSL library must be installed. The easiest way to install this library is to use [`pip`](https://pypi.org/project/pip/) to install the [`pyOpenSSL`](https://www.pyopenssl.org/) library:

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

client = Erkle('erklebot','chat.freenode.net',port=7000,ssl=True)
client.connect()
```

# Another IRC library? Why not use Twisted/irclib/...?
I wanted an IRC library with as few requirements as possible, and didn't require subclassing. I also wanted a client that was small enough to be bundled with an application, rather than requiring a user to install it through [`pip`](https://pypi.org/project/pip/) or some other package manager. Last, I wanted a library that wasn't focused on writing IRC bots or writing IRC clients; I wanted a library that would work for any IRC-related activity.  Since I couldn't find this library, I decided to write Erkle.

# Single file version

The entire library has been "compressed" into a single Python file, [erklelib.py](https://github.com/nutjob-laboratories/erkle/raw/master/erklelib.py), that you can bundle with your applications. The code has not been "minimized", compressed, or otherwise changed, just compiled into a single file. Using it is just as easy as using **Erkle**; just change the import line to `from erklelib import *`.

# Documentation
**Erkle**'s documentation is available [here](https://github.com/nutjob-laboratories/erkle/blob/master/documentation/Erkle-IRC-Library.pdf).

# The author

My name's Dan Hetrick, and I approve of this library :-)