
from erkle.common import *

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " IRC Client"

NO_NICKNAME_IN_DICT_ERROR = "Key 'nickname' missing from configuration dict"
NO_SERVER_IN_DICT_ERROR = "Key 'server' missing from configuration dict"
NO_SSL_ERROR = "SSL/TLS is not available. Please install pyOpenSSL."
DISCONNECTED_ERROR = "Disconnected from the server"
SEND_MESSAGE_ERROR = "Cannot send message: disconnected from the server"
NOT_STARTED_ERROR = "Connection not started; can't send message '{}'"

ERROR_WORD = "Error"
UNKNOWN_ERROR = "Unknown error"