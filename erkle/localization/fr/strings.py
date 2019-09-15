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

DEFAULT_REALNAME = APPLICATION_NAME + " " + ERKLE_VERSION + " client IRC"

NO_NICKNAME_IN_DICT_ERROR = "Clé 'nickname' manquante dans le dictionnaire de configuration."
NO_SERVER_IN_DICT_ERROR = "Clé 'server' manquante dans le dictionnaire de configuration."
NO_SSL_ERROR = "SSL/TLS n'est pas disponible. Veuillez installer pyOpenSSL."
DISCONNECTED_ERROR = "Déconnecté du serveur."
SEND_MESSAGE_ERROR = "Impossible d'envoyer un message: déconnecté du serveur."
NOT_STARTED_MESSAGE_ERROR = "Connexion non établie ne peut pas envoyer le message '{}'"
NOT_THREADED_ERROR = "La connexion n'a pas été démarrée avec spawn()! En sortant..."
NO_SOCKET_ERROR = "Le socket n'a pas été créé, la connexion n'a pas été démarrée."
NOT_STARTED_ERROR = "La connexion n'a pas été démarrée."
WRONG_VARIABLE_TYPE = "Type de variable incorrect pour '{key}' ({rec} reçu, {exp} attendu)."

ERROR_WORD = "Erreur"
UNKNOWN_ERROR = "Erreur inconnue"