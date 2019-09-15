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

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " IRC Client"

NO_NICKNAME_IN_DICT_ERROR = "Key 'nickname' missing from configuration dict."
NO_SERVER_IN_DICT_ERROR = "Key 'server' missing from configuration dict."
NO_SSL_ERROR = "SSL/TLS is not available. Please install pyOpenSSL."
DISCONNECTED_ERROR = "Disconnected from the server."
SEND_MESSAGE_ERROR = "Cannot send message: disconnected from the server."
NOT_STARTED_MESSAGE_ERROR = "Connection not started; can't send message '{}'"
NOT_THREADED_ERROR = "Connection was not started with spawn()! Exiting..."
NO_SOCKET_ERROR = "Socket has not been created, connection has not been started."
NOT_STARTED_ERROR = "Connection not started."
WRONG_VARIABLE_TYPE = "Wrong variable type for '{key}' (received {rec}, expected {exp})."

ERROR_WORD = "Error"
UNKNOWN_ERROR = "Unknown error"