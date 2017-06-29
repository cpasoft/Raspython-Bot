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
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import MessageEntity, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async

# Librería para el log
import logging

# Librerías del sistema
import os

# Librería regex para filtrar textos
import re

# Librería números enteros aleatorios
from random import randint

# Librería de tiempo, para pausas y demás
from time import sleep
import datetime

# Librería json
import json

# Librería para el wrapping de librerías (decoración)
from functools import wraps

# Importamos las constantes desde el fichero correspondiente
# Las importamos una a una por claridad y para saber cuales añadimos nuevas
from constantes import TOKEN, LOG_FILE, GROUPS_ID, HASHTAG_FILE, ADMINS, START, END, HASHTAG, ANTIFLOOD, ANTIFLOOD_FILE
from constantes import ANTIFLOOD_MINUTES, ANTIFLOOD_TAG, ANTIFLOOD_TAG_FILE

# Variables globales:
# Semáforo para ficheros. Usado para controlar la grabación de ficheros en modo asíncrono
semaforo = {
    HASHTAG: False,
    ANTIFLOOD: False,
    ANTIFLOOD_TAG: False
}

# Inicializamos el subsistema de log para nuestro bot. Todos los errores y las informaciones irán a este fichero.
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Control del semáforo para grabación de ficheros
def switch_semaforo(estado, fichero):
    global semaforo
    # Intento de inicio de grabación
    if estado == START:
        #     Esperamos a tener el semáforo libre para pillar hueco
        while semaforo[fichero]:
            # Esperamos un tiempo aleatorio de 0 a 10
            sleep(randint(1, 100) / 100)
        # Cuando lo conseguimos, pillamos
        semaforo[fichero] = True
    # Si queremos cerrar el semáforo...
    else:
        semaforo[fichero] = False


# Decorador para comprobar si un usuario está autorizado a usar una función (Comandos Admin)
def authorized(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.message.chat_id
        # Sólo funcionará si se envía desde privado. En público no funcionan los comandos de Admin
        if chat_id not in GROUPS_ID.values():
            # Si el usuario no es admin, registramos el intento, le respondemos que no puede y anulamos
            if user_id not in ADMINS:
                logger.info("Intento de ejecución de un comando privilegiado por el Usuario: {}.".format(user_id))
                update.message.reply_text("Lo siento, no tienes permiso para ejecutar este comando.")
                return
            # Si sí que es admin, entonces la ejecutamos
            return func(bot, update, *args, **kwargs)
        # Si lo intenta ejecutar en el grupo, no lo permitimos.
        else:
            return
    return wrapped


# Decorador para comprobar si un comando se ha ejecutado repetidamente para no permitirlo (AntiFlood)
def antiflood(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.message.chat_id
        name_func = func.__name__
        # Si se ejecuta desde el grupo comprobaremos el flood
        if chat_id in GROUPS_ID.values():
            funciones_times = read_json(ANTIFLOOD_FILE)
            # Si el fichero existe y no está vacío y el canal existe
            if funciones_times and str(chat_id) in funciones_times:
                # Si la función ya está registrada en el fichero
                if name_func in funciones_times[str(chat_id)]:
                    # Si la función ha sido ejecutada en los últimos minutos, no ejecutamos la función
                    hora = datetime.datetime.strptime(funciones_times[str(chat_id)][name_func], "%d-%m-%Y %H:%M")
                    if hora > datetime.datetime.now() - datetime.timedelta(minutes=ANTIFLOOD_MINUTES):
                        return
            # Si aún no se ha registrado el canal, lo registramos
            else:
                funciones_times[str(chat_id)] = {}
            # Y registramos la función ejecutada y la hora
            funciones_times[str(chat_id)][name_func] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            graba_json(ANTIFLOOD, ANTIFLOOD_FILE, funciones_times)
            return func(bot, update, *args, **kwargs)
        # Si se envía desde privado, la ejecutamos siempre. Si se quiere hacer flood a si mismo... :-p
        else:
            return func(bot, update, *args, **kwargs)

    return wrapped


# Función para comprobar si la impresión de un hashtag es muy repetida en tiempo (Antiflood)
def antiflood_tags(chat_id, tag):
    # Si la ejecución del trag se hace en los grupos
    if chat_id in GROUPS_ID.values():
        tag_times = read_json(ANTIFLOOD_TAG_FILE)
        # Si el fichero existe y no está vacío y el canal existe
        if tag_times and str(chat_id) in tag_times:
            # Si el tag ya está registrado en el fichero
            if tag in tag_times[str(chat_id)]:
                # Si el tag ha sido ejecutada en los últimos minutos, no ejecutamos la impresión
                hora = datetime.datetime.strptime(tag_times[str(chat_id)][tag], "%d-%m-%Y %H:%M")
                if hora > datetime.datetime.now() - datetime.timedelta(minutes=ANTIFLOOD_MINUTES):
                    return False
        # Si ese tag o grupo aún no estaba registrado, lo registramos
        else:
            tag_times[str(chat_id)] = {}
        # Grabamos la hora de ejecución del tag correspondiente
        tag_times[str(chat_id)][tag] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        graba_json(ANTIFLOOD_TAG, ANTIFLOOD_TAG_FILE, tag_times)
        return True
    # Si se envía desde privado, la ejecutamos siempre. Si se quiere hacer flood a si mismo... :-p
    else:
        return True


# Función de ayuda. Aquí iremos poniendo todos los comandos y opciones de los que vayamos dotando al bot.
# Intenta enviarla por privado, si no puede, la envía al grupo con enlace al bot + AntiFlood
@antiflood
def bot_help(bot, update):
    # Obtenemos el ID del chat desde donde nos hablan...
    chat_id = update.message.chat_id
    # Y el privado del usuario
    user_id = update.message.from_user.id
    # Intentamos enviarle la ayuda por privado...
    try:
        bot.send_message(chat_id=user_id, text="""
ℹ️ COMANDOS Y FUNCIONES DISPONIBLES ℹ️

▪️/canales
Muestra la relación de canales de Raspito's Family
▪️ /normas
Muestra las reglas comunes a los canales de Raspito's Family
▪️/tags
Muestra la relación de tags con información disponibles
""")
        # Si el usuario es un Admin, le mandamos la extensión de ayuda a administradores
        if user_id in ADMINS:
            bot.send_message(chat_id=user_id, text="🔐 ***ADMIN DETECTED***‼\n"
                                      "Como admin, tienes derecho a añadir, editar y borrar tags.\n"
                                      "Envía /tags para obtener más ayuda sobre cómo hacerlo.",
                                      parse_mode=ParseMode.MARKDOWN)
    # Si no hemos podido enviarlo por privado...
    except:
        update.message.reply_text("Para acceder a la ayuda, pincha en <a href='http://t.me/RaspythonBot'>"
                                  "ESTE ENLACE</a> e iníciame...",
                                  parse_mode=ParseMode.HTML)


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
@antiflood
def canales(bot, update):
    # Enviamos la lista de canales de la Raspito's Family con control Antiflood
    update.message.reply_text("🔸 Relación de los canales de la Raspito's Family 👨‍👩‍👧‍👦\n\n"
                              "▫️@GrupoRaspberryPI\n"
                              "Canal precursor de la Raspito's Family. Dialoga sobre los aspectos generales "
                              "sobre la Raspberry PI, como donde comprarla, que accesorios son recomendables, "
                              "dudas sobre configuración, etc. En definitiva, todo lo relacionado sobre nuestras "
                              "PI que no abarquen más específicamente el resto de canales de la familia.\n\n"
                              "▫️@RaspberryPiMediacenters\n"
                              "Canal enfocado al uso y disfrute de nuestras Raspberry Pi como centro multimedia.\n\n"
                              "▫ @RaspberryPiEmuladores\n"
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
@antiflood
def normas(bot, update):
    # Enviamos las reglas del grupo con control Antiflood
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
# De momento sólo responde a un pequeño easteregg en honor a "Raspito". Tiene control de flood
@antiflood
@run_async
def trata_texto(bot, update):
    # chat_id = update.message.chat_id
    # user_id = update.message.from_user.id
    texto = update.message.text

    if re.search(r"(?i)qu[eé] es raspito\b", texto):
        update.message.reply_text("...son los padres")


# Función en la que tratamos los hashtags de los mensajes
@run_async
def parsing_hashtag(bot, update):
    chat_id = update.message.chat_id
    # user_id = update.message.from_user.id
    hashtags = update.message.parse_entities('hashtag')
    # Pasamos los hashtags a minúsculas y eliminamos duplicados
    hashtags = set([x.lower() for x in list(hashtags.values())])
    # Leemos la relación de tags de nuestro fichero
    # Ahora mismo sólo soportamos un HASHTAG_FILE, pero lo suyo es tener tantos HASHTAG_FILE como canales diferentes
    # para que cada grupo pueda administrar sus propios tags. Eso obliga a cambiar las funciones de creación de tags.
    bot_tags = read_json(HASHTAG_FILE)
    # Si no a habido problemas y tenemos tags en el fichero, los procesamos
    if bot_tags:
        for h in sorted(hashtags):
            if h in bot_tags:
                if antiflood_tags(chat_id, h):
                    update.message.reply_text("***#{}***\n{}".format(h[1:].capitalize(), bot_tags[h]),
                                              parse_mode=ParseMode.MARKDOWN, quote=False,
                                              disable_web_page_preview=True)


# Función que abre el JSON de los Hashtag y devuelve su contenido. En caso de error devolvemos nulo.
def read_json(file):
    # Si el fichero no existe, devolvemos un diccionario vacío
    if not os.path.isfile(file):
        return {}
    # Intentamos abrirlo y retornamos el contenido
    try:
        with open(file, "r") as f:
            return json.load(f)
    # Si no podemos, retornamos nulo
    except:
        return None


# Función para añadir tags al fichero
def editing_tags(bot, update):
    # Separamos los comandos
    comando = update.message.text_markdown
    chat_id = update.message.chat_id
    # Si sólo ha mandado el comando, mostramos la ayuda
    if not len(comando.split()) == 1:
        # Si el comando es el de "añadir"
        if comando.split()[1].lower() == "add":
            # Si faltan parámetros
            if len(comando.split()) < 3 or not len(comando.split("@@")) == 2:
                tagtoadd = ""
            else:
                # Separamos tag del texto
                tagtoadd = " ".join(comando.split()[2:]).split("@@")

            # Si no lo ha mandado correctamente formateado
            if not len(tagtoadd) == 2 or not len(tagtoadd[0].split()) == 1:
                update.message.reply_text("⚠️ Recuerda, `/tags add #etiqueta@@texto`\n\n",
                                          parse_mode=ParseMode.MARKDOWN)
                return

            # Separamos tag del texto
            tag = comando.split("@@")[0].split()[2]
            text = comando.split("@@")[1]
            # Comprobamos que es un tag
            if tag[0] == "#":
                # grabamos(tag,texto)
                if graba_tag(tag.lower(), text):
                    update.message.reply_text("Actualización de hastags correcta 👍🏼")
                    return
                else:
                    update.message.reply_text("❌ Problema en la grabación de los hashtags")
                    logger.info("Problema en la grabación de los hashtags en editing_tags")
                    return
            else:
                update.message.reply_text("⚠️No has enviado un hashtag. Te faltó la #")
                return
        elif comando.split()[1].lower() == "list" and len(comando.split()) == 2:
            print_list(bot, update)
            return

        elif comando.split()[1].lower() == "del" and len(comando.split()) == 3:
            tag = comando.split()[2]
            if tag[0] == "#":
                keyboard = [[InlineKeyboardButton("Si", callback_data='Si_delete'),
                             InlineKeyboardButton("No", callback_data='No_delete')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=chat_id, text='¿Quieres eliminar el tag {}?:'
                                 .format(tag), reply_markup=reply_markup)
            else:
                update.message.reply_text("⚠️No has enviado un hashtag. Te faltó la #")
            return

    # Si hemos llegado aquí, es que el comando estaba mal formado.
    update.message.reply_text("📌 El uso de /tags es el siguiente:\n\n"
                              "▫️Para añadir o editar un hashtag existente usa:\n`/tags add #etiqueta@@texto`\n"
                              "▫ Para eliminar un hashtag usa:\n`/tags del #etiqueta`\n"
                              "▫ Para listar los hashtag establecidos usa:\n`/tags list`\n",
                              parse_mode=ParseMode.MARKDOWN)
    return


# Función que realiza la grabación del JSON con control asíncrono
# Recibe en tipo la variable del semáforo, el fichero y los datos a guardar
def graba_json(tipo, file, datos):
    # Solicitamos permiso al semáforo
    switch_semaforo(START, tipo)
    try:
        with open(file, "w") as f:
            json.dump(datos, f)
        # Liberamos el semáforo
        switch_semaforo(END, tipo)
        return True
    except:
        logger.info("Error de grabación al grabar {}.".format(file))
        # Liberamos el semáforo
        switch_semaforo(END, tipo)
        return False


# Función que realiza la grabación del JSON de los tags con control asíncrono
# Recibo el tag a guardar y el texto del mismo
def graba_tag(tag, texto):
    # Solicitamos permiso al semáforo
    switch_semaforo(START, HASHTAG)
    # Leemos las tags del fichero
    bot_tags = read_json(HASHTAG_FILE)
    # Comprobamos si la lectura ha tenido éxito
    if bot_tags is None:
        logger.info("Error de lectura del hashtagfile en graba_tag.")
        # Liberamos el semáforo
        switch_semaforo(END, HASHTAG)
        return False
    # Actualizamos o creamos el tag con el texto
    bot_tags[tag] = texto
    try:
        with open(HASHTAG_FILE, "w") as f:
            json.dump(bot_tags, f)
        # Liberamos el semáforo
        switch_semaforo(END, HASHTAG)
        return True
    except:
        logger.info("Error de lectura del hashtagfile en graba_tag.")
        # Liberamos el semáforo
        switch_semaforo(END, HASHTAG)
        return False


# Función que recorre el fichero de tags y los manda formateados en columnas
@antiflood
@run_async
def list_tags(bot, update):
    # Si lo manda uno de los admins por privado
    if update.message.chat_id in ADMINS:
        # Le mando a la función avanzada
        editing_tags(bot, update)
    else:
        print_list(bot, update)


def print_list(bot, update):
    # Leemos la relación de tags de nuestro fichero
    bot_tags = read_json(HASHTAG_FILE)
    # Si no a habido problemas y tenemos tags en el fichero, los procesamos
    if bot_tags:
        update.message.reply_text("👇🏼 A continuación la relación de tags registrados 👇🏼", quote=False)
        i = 0
        tag_text = ""
        for h in sorted(bot_tags):
            i += 1
            tag_text += "#️⃣" + " " + "`" + h[1:].upper() + "`" + "\n"
            if i > 20:
                update.message.reply_text(tag_text, parse_mode=ParseMode.MARKDOWN, quote=False)
                i = 0
                tag_text = ""
        if i:
            update.message.reply_text(tag_text, parse_mode=ParseMode.MARKDOWN, quote=False)
    else:
        update.message.reply_text("😣 Actualmente no hay tags registrados")


def delete_tag(bot, update):
    query = update.callback_query
    tag = "#" + update.callback_query.message.text.split("#")[1][:-2]
    if query.data in "Si_delete":
        # Solicitamos permiso al semáforo
        switch_semaforo(START, HASHTAG)
        # Leemos las tags del fichero
        bot_tags = read_json(HASHTAG_FILE)
        # Comprobamos si la lectura ha tenido éxito
        if bot_tags is None:
            logger.info("Error de lectura del hashtagfile en delete_tag.")
            # Liberamos el semáforo
            switch_semaforo(END, HASHTAG)
            bot.edit_message_text(text="❌ Problema de lectura del fichero hashtagfile al borrar el tag",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return

        # Buscamos primero el tag, y si no está, retornamos error
        if tag.lower() not in bot_tags:
            switch_semaforo(END, HASHTAG)
            bot.edit_message_text(text="⚠ El tag no se encuentra en la lista. Abortamos...",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return

        # Si está, entonces lo borramos
        del bot_tags[tag]
        # Y grabamos
        try:
            with open(HASHTAG_FILE, "w") as f:
                json.dump(bot_tags, f)
            # Liberamos el semáforo
            switch_semaforo(END, HASHTAG)
            bot.edit_message_text(text="♻️El tag ha sido eliminado correctamente de la lista! 🗑",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return
        except:
            logger.info("Error de lectura del hashtagfile en graba_tag.")
            # Liberamos el semáforo
            switch_semaforo(END, HASHTAG)
            bot.edit_message_text(text="❌ Problema al guardar el fichero hashtagfile al borrar el tag",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return
    else:
        bot.edit_message_text(text="✋🏼 Anulado el borrado del tag... ✋🏼",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)


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
    dispatcher.add_handler(CommandHandler("tags", list_tags))

    # Capturador de nuevos miembros
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bienvenida))

    # Capturador de comandos no reconocidos
    dispatcher.add_handler(MessageHandler(Filters.command, comando_invalido))

    # Capturador de textos. Capturaremos aquello que no sean comandos explícitos
    # Cuando contienen hashtags
    dispatcher.add_handler(MessageHandler(Filters.entity(MessageEntity.HASHTAG), parsing_hashtag))
    # Cuando es texto
    dispatcher.add_handler(MessageHandler(Filters.text, trata_texto))

    # Capturador del menú de borrado de tags (Si y No)
    raspython_bot.dispatcher.add_handler(CallbackQueryHandler(delete_tag, pattern="Si_delete|No_delete"))

    # Arrancamos el bot, empezamos a capturar peticiones
    # Con clean ignoramos los mensajes pendientes...
    raspython_bot.start_polling(clean=True)
    #  Y lo dejamos esperando
    raspython_bot.idle()


if __name__ == "__main__":
    main()
