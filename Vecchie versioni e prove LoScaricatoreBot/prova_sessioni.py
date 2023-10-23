import telebot
import pickle

# Token del tuo bot Telegram
TOKEN = '6298767518:AAEl_6YTb6s_rk0BGvNbl0B5V6EnEftnuug'

# Crea un oggetto bot
bot = telebot.TeleBot(TOKEN)

# Dizionario per memorizzare le sessioni degli utenti
user_sessions = {}

# Gestisce il comando /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id

    # Verifica se l'utente ha una sessione attiva
    if user_id in user_sessions:
        session = user_sessions[user_id]
        language = session.get('language', None)
        print(language)
        if language:
            response = "La tua lingua attuale è: " + language
        else:
            response = "Non hai selezionato una lingua."
    else:
        session = {}
        response = "Seleziona la lingua / Select language:"

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = telebot.types.KeyboardButton("Italiano")
    item2 = telebot.types.KeyboardButton("English")
    markup.add(item1, item2)
    msg = bot.send_message(user_id, response, reply_markup=markup)
    user_sessions[user_id] = session  # Aggiorna o crea la sessione utente
    #bot.register_next_step_handler(msg, choose_language)

# Gestisce la scelta della lingua
def choose_language(message):
    user_id = message.chat.id
    language = message.text.lower()
    session = user_sessions.get(user_id, {})
    session['language'] = language
    user_sessions[user_id] = session

    with open("user_data.pkl", "wb") as file:
        pickle.dump(user_sessions, file)

    if language == 'italiano':
        response = "Ciao!"
    elif language == 'english':
        response = "Hello!"
    else:
        response = "Lingua non supportata / Language not supported"
    bot.send_message(user_id, response)

# Gestisce eventuali altri messaggi
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Comando non riconosciuto / Unrecognized command")

# Esegui il bot
bot.polling()
