#!/usr/bin/python3
# -*- coding: utf-8 -*-
#  RaspythonBot (c) 2017 - Raspython Group
#
#  Bot de moderación creado por y para el grupo de Telegram @Raspython
# t.me/raspython
#
#

##########################################################################
##########################################################################


# Librería PTB
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Librería para el log
import logging

# Librería regex para filtrar textos
import re

# Importamos las constantes desde el fichero correspondiente
from constantes import TOKEN, LOG_FILE, GROUPS_ID

# Inicializamos el subsistema de log para nuestro bot. Todos los errores y las informaciones irán a este fichero.
logging.basicConfig(filemode=LOG_FILE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Función temporal. Es una forma de recoger y mostrar el ID de un usuario o un grupo para luego poder usarlo.
# Esta función no estará en el bot definitivo.
def chatid(bot, update):
    # Obtenemos el ID del chat desde donde nos hablan...
    chat_id = update.message.chat_id
    # La ayuda sólo la mostraremos si se ejecuta en privado. Si se hace en uno de los canales la ignoraremos.
    update.message.reply_text("El ChatID de este usuario/grupo es {}".format(chat_id))


# Función de ayuda. Aquí iremos poniendo todos los comandos y opciones de los que vayamos dotando al bot. Lo pongo como
# primera función para un fácil acceso a ella, ya que estará en constante crecimiento...
def bot_help(bot, update):
    # Obtenemos el ID del chat desde donde nos hablan...
    chat_id = update.message.chat_id
    # La ayuda sólo la mostraremos si se ejecuta en privado. Si se hace en uno de los canales la ignoraremos.
    if chat_id not in GROUPS_ID.values():
        update.message.reply_text("""
ℹ️ COMANDOS Y FUNCIONES DISPONIBLES ℹ️

▪️ /normas
Muestra las reglas comunes a los canales de Raspito's Family
▪️/canales
Muestra la relación de canales de Raspito's Family
""")
    else:
        update.message.reply_text("❗️La ayuda la ofrezco por privado ❗\nÁbreme un privado y envía /help de nuevo...")


# Función de arranque del Bot. Será lo que se muestre cuando un usuario inicie el Bot en privado.
def start(bot, update):
    # Obtenemos el ID del chat desde donde nos hablan...
    chat_id = update.message.chat_id
    # La ayuda sólo la mostraremos si se ejecuta en privado. Si se hace en uno de los canales la ignoraremos.
    if chat_id not in GROUPS_ID.values():
        update.message.reply_text("🤖 Bienvenido al RaspythonBot 🤖\n"
                                  "Bot creado y pensado para dar soporte al grupo @Raspython\n"
                                  "t.me/Raspython\n"
                                  "Pulsa /help para obtener ayuda sobre lo que puedes hacer")


# Función que muestra la relación de canales de la Raspito's Family
def canales(bot, update):
    # En principio este comando lo mostraremos en todos los canales. Si vemos que hay mucho flood ya lo limitaremos.
    update.message.reply_text("🔸 Relación de los canales de la Raspito's Family 👨‍👩‍👧‍👦\n\n"
                              "▫️@GrupoRaspberryPI\n"
                              "Canal precursor de la Raspito's Family. Dialoga sobre los aspectos generales "
                              "sobre la Raspberry PI, como donde comprarla, que accesorios son recomendables, "
                              "dudas sobre configuración, etc. En definitiva, todo lo relacionado sobre nuestras "
                              "PI que no abarquen más específicamente el resto de canales de la familia.\n\n"
                              "▫️@RaspberryPiMediacenters\n"
                              "Canal enfocado al uso y disfrute de nuestras Raspberry Pi como centro multimedia.\n\n"
                              "▫ @RaspberryPiEmuladores"
                              "Canal dedicado a la temática sobre emulación en nuestras Raspberry Pi. Configura tu "
                              "pequeña Pi como un centro de juego arcade. Disfruta con la emulación!.\n\n"
                              "▫ @Raspython\n"
                              "Grupo para debatir, dialogar y preguntar sobre todo lo relacionado con la programación "
                              "en Python y Raspberry. Este Bot es precisamente un proyecto desarrollado en este canal. "
                              "Únete y disfruta.\n\n▫ @RaspberryPiOfftopic\n"
                              "¿Te apetece hablar con los compañeros de la Raspito's family sobre cualquier otro "
                              "tema?, pues este es tu canal. Entra charla, comparte y disfruta con el resto de "
                              "compañeros sin límite de temática. (Contenido sexual explícito, violento y de temáticas "
                              "similares está prohibido)")


# Función que tiene como objeto mostrar las reglas del grupo
# De momento las ponemos estáticas en el código, pero la idea es que sean modificables por los moderadores, por lo que
# en un futuro residirán en un fichero
def normas(bot, update):
    # En principio este comando lo mostraremos en todos los canales. Si vemos que hay mucho flood ya lo limitaremos.
    update.message.reply_text("📜 Las reglas de este grupo son muy sencillas...\n\n"
                              "⛔️Nada de sexo explícito, ni política, ni religión, ni nada no relacionado "
                              "con la temática del canal.\n"
                              "🚫 Tampoco están permitidos los enlaces a otros grupos o páginas webs que cumplan "
                              "los criterios anteriormente descritos.\n"
                              "❓ En caso de dudas, consultar con cualquier administrador del grupo.\n\n"
                              "🤙🏼 Como último requisito, pasarlo bien, disfrutar, compartir y que fluya el buen rollo")


# En esta función trataremos los comandos no reconocidos. De momento lo dejamos en "pass" para ignorarlos
def comando_invalido(bot, update):
    pass


# Función en la que filtraremos los datos enviados por el usuario y que trataremos según corresponda
def trata_texto(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    texto = update.message.text
    # En el siguiente ejemplo, si alguien mete la palabra bot, responderemos con un mensaje y el id del usuario y grupo
    # Es un ejemplo temporal. Aquí irán los tratamientos de envíos a otros canales, y los lanzadores a través de tags
#    if re.search(r"(?i)\bbot\b", texto):
#        update.message.reply_text("¿Me has nombrado?\n"
#                                  "Que sepas que me hablas desde {} y tu ID es {}\n".format(chat_id, user_id))
    if re.search(r"(?i)qu[eé] es raspito\b", texto):
         update.message.reply_text("...son los padres")


def bienvenida(bot, update):
    chat_id = update.message.chat_id
    if chat_id == GROUPS_ID["Raspython"]:
        update.message.reply_text("Bienvenido al grupo de Raspython... DISFRUTA Y PARTICIPA! 👋🏼\n"
                                  "Ábreme un privado para obtener información...")


def main():
    # Inicializamos nuestro bot
    raspython_bot = Updater(token=TOKEN)
    # Generamos el dispatcher para recoger los comandos y textos del chat
    dispatcher = raspython_bot.dispatcher

    # Definición de los comandos
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", bot_help))
    dispatcher.add_handler(CommandHandler("canales", canales))
    dispatcher.add_handler(CommandHandler("normas", normas))
    dispatcher.add_handler(CommandHandler("chatid", chatid))

    # Capturador de nuevos miembros
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bienvenida))

    # Capturador de comandos no reconocidos
    dispatcher.add_handler(MessageHandler(Filters.command, comando_invalido))

    # Capturador de textos. Capturaremos aquello que no sean comandos explícitos
    dispatcher.add_handler(MessageHandler(Filters.text, trata_texto))

    # Arrancamos el bot, empezamos a capturar peticiones
    # Con clean ignoramos los mensajes pendientes...
    raspython_bot.start_polling(clean=True)
    #  Y lo dejamos esperando
    raspython_bot.idle()


if __name__ == "__main__":
    main()
