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

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " IRC-Client"

NO_NICKNAME_IN_DICT_ERROR = "Der Schlüssel 'nickname' fehlt im Konfigurationswörterbuch."
NO_SERVER_IN_DICT_ERROR = "Der Schlüssel 'server' fehlt im Konfigurationswörterbuch."
NO_SSL_ERROR = "SSL/TLS is not available. Please install pyOpenSSL."
DISCONNECTED_ERROR = "Verbindung zum Server getrennt."
SEND_MESSAGE_ERROR = "Nachricht kann nicht gesendet werden: Verbindung zum Server getrennt."
NOT_STARTED_MESSAGE_ERROR = "Verbindung nicht gestartet; kann die Nachricht '{}' nicht senden."
NOT_THREADED_ERROR = "Verbindung wurde nicht mit spawn() gestartet! Verlassen..."
NO_SOCKET_ERROR = "Socket wurde nicht erstellt, Verbindung wurde nicht gestartet."
NOT_STARTED_ERROR = "Verbindung nicht gestartet."

ERROR_WORD = "Error"
UNKNOWN_ERROR = "Unbekannter Fehler"