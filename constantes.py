#  TOKEN de nuestro bot. Es entregado por BotFather.
TOKEN = "<PONER AQUI EL TOKEN DEL BOT>"

#  Relación de los Chat_ID de los grupos de la Raspito's Family
GROUPS_ID = {
    "Raspython": -1001122218457,
    "General": -1001027822398,
    "Mediacenters": -1001088073949,
    "Emuladores": -1001081864192,
    "Off-topic": -1001051912425,
}

# Tiempo para el antiflood
ANTIFLOOD_MINUTES = 15

#  Relación de los User_ID de las personas autorizadas a hacer tareas restringidas en el Bot. (AkA moderadores)
ADMINS = [<Aquí van los IDs de los admins/editores>]

#  Ubiación del fichero de Log de nuestro Bot. Importante que el usuario con el que se corra el bot tenga derechos de
#  escritura sobre dicho fichero.
LOG_FILE = "/var/log/RaspythonBot.log"

# Ubicación del fichero de hashtags
HASHTAG_FILE = "./databases/hashtags.json"
ANTIFLOOD_FILE = "./databases/antiflood.json"
ANTIFLOOD_TAG_FILE = "./databases/antiflood_tag.json"

# Constantes para semáforo:
START = True
END = False
HASHTAG = 1
ANTIFLOOD = 2
ANTIFLOOD_TAG = 3


