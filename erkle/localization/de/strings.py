
from erkle.common import *

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " IRC-Client"

NO_NICKNAME_IN_DICT_ERROR = "Der Schlüssel 'nickname' fehlt im Konfigurationswörterbuch"
NO_SERVER_IN_DICT_ERROR = "Der Schlüssel 'server' fehlt im Konfigurationswörterbuch"
NO_SSL_ERROR = "SSL/TLS is not available. Please install pyOpenSSL."
DISCONNECTED_ERROR = "Verbindung zum Server getrennt"
SEND_MESSAGE_ERROR = "Nachricht kann nicht gesendet werden: Verbindung zum Server getrennt"
NOT_STARTED_ERROR = "Verbindung nicht gestartet; kann die Nachricht '{}' nicht senden"

ERROR_WORD = "Error"
UNKNOWN_ERROR = "Unbekannter Fehler"