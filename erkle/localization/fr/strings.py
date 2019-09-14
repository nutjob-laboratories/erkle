
from erkle.common import *

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " client IRC"

NO_NICKNAME_IN_DICT_ERROR = "Clé 'nickname' manquante dans le dictionnaire de configuration"
NO_SERVER_IN_DICT_ERROR = "Clé 'server' manquante dans le dictionnaire de configuration"
NO_SSL_ERROR = "SSL/TLS n'est pas disponible. Veuillez installer pyOpenSSL"
DISCONNECTED_ERROR = "Déconnecté du serveur"
SEND_MESSAGE_ERROR = "Impossible d'envoyer un message: déconnecté du serveur"
NOT_STARTED_ERROR = "Connexion non établie ne peut pas envoyer le message '{}'"

ERROR_WORD = "Erreur"
UNKNOWN_ERROR = "Erreur inconnue"