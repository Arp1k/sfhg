import os
from threading import Thread
import telebot
from telebot import types
import time

TOKEN = '6893596394:AAFxiXHDJ_QypG6GkXCE9tjUZ7wMn2gcz2U'

bot = telebot.TeleBot(TOKEN)
user_answers = {}
users = {}

def keep_alive():
    while True:
        try:
            bot.get_me()
        except Exception as e:
            print(f"Помилка під час запиту до Telegram API: {e}")
        time.sleep(3600)
bot_running = False
waiting_for_chat_id = False
target_chat_id = None
def run_bot():
    global bot_running
    bot_running = True
    bot.polling()
    bot_running = False
# Стан очікування повідомлення для надсилання
waiting_for_message = False
message_to_send = None
waiting_for_chat_id = False
target_chat_id = None
target_admin_id = None

# Стан очікування повідомлення для надсилання
waiting_for_message = False
message_to_send = None

def is_admin(chat_id):
    return str(chat_id) in ADMINS

@bot.message_handler(commands=['send'])
def handle_send_command(message):
    global waiting_for_chat_id, target_admin_id
    if is_admin(message.chat.id):
        waiting_for_chat_id = True
        target_admin_id = message.chat.id
        bot.reply_to(message, "Надішліть chat_id користувача, якому потрібно надіслати повідомлення або фото.")
    else:
        bot.reply_to(message, "Ви не маєте прав для використання цієї команди.")

@bot.message_handler(func=lambda message: waiting_for_chat_id and is_admin(message.chat.id), content_types=['text'])
def handle_chat_id(message):
    global waiting_for_chat_id, target_chat_id, waiting_for_message
    try:
        chat_id = int(message.text)
        target_chat_id = chat_id
        waiting_for_chat_id = False
        waiting_for_message = True
        bot.reply_to(message, "Надішліть повідомлення або фото, яке потрібно передати користувачеві.")
    except ValueError:
        bot.reply_to(message, "Неправильний chat_id. Спробуйте ще раз.")

@bot.message_handler(func=lambda message: waiting_for_message and is_admin(message.chat.id), content_types=['text', 'photo'])
def handle_message_to_send(message):
    global waiting_for_message, message_to_send
    if message.content_type == 'text':
        message_to_send = message.text
    elif message.content_type == 'photo':
        message_to_send = message.photo[-1].file_id
    waiting_for_message = False
    try:
        if message.content_type == 'text':
            bot.send_message(target_chat_id, message_to_send)
        elif message.content_type == 'photo':
            bot.send_photo(target_chat_id, message_to_send)
        bot.reply_to(message, "Повідомлення успішно надіслано.")
    except Exception as e:
        bot.reply_to(message, f"Помилка під час надсилання повідомлення: {e}")

@bot.message_handler(func=lambda message: message.chat.id == target_chat_id, content_types=['text', 'photo'])
def forward_message_to_admin(message):
    try:
        if message.content_type == 'text':
            bot.forward_message(target_admin_id, message.chat.id, message.message_id)
        elif message.content_type == 'photo':
            bot.forward_message(target_admin_id, message.chat.id, message.message_id)
    except Exception as e:
        print(f"Помилка під час пересилання повідомлення адміністратору {target_admin_id}: {e}")

ADMINS = ['1580990462', '5210739777']
def delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print("Помилка при видаленні повідомлення:", e)

def create_rating_keyboard(callback_prefix):
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f"{callback_prefix}_{i}") for i in range(11)]
    markup.add(*buttons)
    return markup

def send_start_message():
    chat_ids = [1580990462, 5210739777]

    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, "Бот запущений!")
        except Exception as e:
            print(f"Помилка при надсиланні повідомлення адміністратору {chat_id}: {e}")
@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Напишіть, будь ласка, причину звернення:")
    bot.register_next_step_handler(message, handle_help_reason)

def handle_help_reason(message):
    chat_id = message.chat.id
    reason = message.text
    for admin_id in ADMINS:
        bot.send_message(admin_id, f"Користувач з {chat_id} звернувся по такій причині: {reason}")
def create_skin_state_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="🌱1 тип", callback_data="skin_type_dry"),
        types.InlineKeyboardButton(text="🌱2 тип", callback_data="skin_type_normal"),
        types.InlineKeyboardButton(text="🌱3 тип", callback_data="skin_type_1"),
        types.InlineKeyboardButton(text="🌱4 тип", callback_data="skin_type_2"),
        types.InlineKeyboardButton(text="🌱5 тип", callback_data="skin_type_3")
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    users[chat_id] = message.chat.username  # Зберігаємо ім'я користувача у словнику
    user = message.from_user
    if user.username:
        username = user.username
    else:
        username = str(chat_id)

    bot.send_message(1580990462, f"Користувач {username} {chat_id} розпочав опитування.")
    bot.send_message(5210739777, f"Користувач {username} розпочав опитування.")
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton(text='Розпочати', callback_data='start')
    markup.add(btn_start)

    bot.send_message(message.chat.id, "<b>Вітаю</b> 😍\n\n"
                                      "Я допоможу Вам швидко з'ясувати <b>Ваш</b> тип та стан шкіри.\n\n"
                                      "Але перед цим, хочу сказати, <b>що я безмежно вдячна за довіру</b> ☺️\n\n"
                                      "Ця інформація допоможе Вам більш точно розуміти потреби шкіри та вдало підбирати догляд.\n\n"
                                      "<b>Тому пропоную не втрачати час і протестувати Вашу шкіру просто зараз</b> 👇",
                     parse_mode='HTML', reply_markup=markup)

    # Потрібно створити окремий запис у словнику user_answers для кожного користувача
    user_answers[chat_id] = {}

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def callback_query_start(call):
    if call.data == 'start':
        bot.send_message(call.message.chat.id, "<b>Нижче Вам будуть подані описи різних типів шкіри👇</b>\n\n"
                                               "Уважно <b>прочитайте</b> їх <b>та оберіть</b> пункт, який буде найбільш точно описувати Ваші відчуття та вигляд Вашої шкіри.\n\n"
                                               "📎<b>Тип шкіри не дорівнює стан шкіри</b>\n"
                                               "📎<b>Тип шкіри не змінюється протягом життя</b>", parse_mode='HTML')
        delete_message(call.message.chat.id, call.message.message_id)
        time.sleep(9)
        bot.send_message(call.message.chat.id, "Для кращого розуміння наступних пунктів, пропоную ознайомитись із картинками")
        time.sleep(2)
        file_id = ' photo_2024-04-08_17-40-36.jpg'
        photo = open('photo_2024-04-08_17-40-36.jpg', 'rb')
        photo1 = open('photo_2024-04-08_17-40-32.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo1)
        bot.send_photo(call.message.chat.id, photo,"Відкриті комедони")
        time.sleep(5)
        photo2 = open('photo_2024-04-08_18-02-54.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo2,"Закриті комедони")
        time.sleep(5)
        photo3 = open('photo_2024-04-08_18-03-01.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo3,"Сальні нитки")
        time.sleep(5)
        photo4 = open('photo_2024-04-08_18-03-14.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo4,"Міліуми")
        time.sleep(5)
        photo5 = open('photo_2024-04-08_18-03-24.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo5,"Пори")
        time.sleep(5)
        bot.send_message(call.message.chat.id, "<b>🌱1 тип</b>\n"
                                               "⦁ шкіра матова, якщо одразу не нанести зволоження, мало власних ліпідів;\n"
                                               "⦁ після очищення хочеться одразу нанести крем;\n"
                                               "⦁ немає проблем з комедонами (поодинокі можливі);\n"
                                               "⦁ пори маловиражені (з віком вираженість пор зростає у всіх типів шкіри).",
                          parse_mode='HTML')
        time.sleep(9)
        bot.send_message(call.message.chat.id, "<b>🌱2 тип</b>\n"
                                               "⦁ природний помірний блиск (ні суха, ні жирна);\n"
                                               "⦁ немає дискомфорту, відчуття сухості і нагальної потреби у зволоженні після очищення;\n"
                                               "⦁ немає проблеми з комедонами (одиничні можуть бути, як і висипи), всі процеси відбуваються коректно.",
                          parse_mode='HTML')
        time.sleep(9)
        bot.send_message(call.message.chat.id, "<b>🌱3 тип</b>\n"
                                               "⦁ шкіра має надмірний жирний блиск;\n"
                                               "⦁ легко обходиться без зволоження після очищення;\n"
                                               "⦁ себум вільно виходить з проток сальних залоз, рідко є комедони або одиничні.",
                          parse_mode='HTML')
        time.sleep(9)
        bot.send_message(call.message.chat.id, "<b>🌱4 тип</b>\n"
                                               "⦁ себум густий і складно виходить з проток сальних залоз (через це є зневоднені, сухі ділянки);\n"
                                               "⦁ проблема закритих комедонів;\n"
                                               "⦁ часте відчуття стягнутості, лущення, порушений захисний бар'єр.",
                          parse_mode='HTML')
        time.sleep(9)
        bot.send_message(call.message.chat.id, "<b>🌱5 тип</b>\n"
                                               "⦁ є ділянки із комедонами, із запаленнями;\n"
                                               "⦁ є жирні та зневоднені ділянки.", parse_mode='HTML')
        time.sleep(6)
        bot.send_message(call.message.chat.id, "Прочитавши опис кожного типу, <b>оберіть пункт</b>, який буде найбільш точно характеризувати Ваш тип шкіри 👇", reply_markup=create_skin_state_keyboard(), parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('skin_type_'))
def callback_query_skin_type(call):
    chat_id = call.message.chat.id
    user_answers[chat_id] = {"skin_type": call.data.split('_')[-1]}
    bot.send_message(chat_id, "<b>Дякую 🤍</b>\n"
                              "Ваша відповідь врахована", parse_mode='HTML')
    time.sleep(3)
    bot.send_message(chat_id, "Ідемо далі ✅", parse_mode='HTML')
    time.sleep(2)

    bot.send_message(chat_id, "Ми вже з'ясували, що <b>тип шкіри сталий,</b> а от\n"
                              "<b>Стан шкіри може періодично змінюватись,</b>\n"
                              "оскільки на нього впливає догляд, навколишнє середовище, стреси.", parse_mode='HTML')
    time.sleep(9)
    bot.send_message(chat_id, "Ви можете відчувати, що Ваша шкіра перебуває у <b>зневодненому стані 💦</b> незалежно від Вашого типу шкіри.\n\n"
                              "Це стан, коли <b>Ви відчуваєте</b>\n"
                              "⦁ сухість\n"
                              "⦁ можливе лущення\n"
                              "⦁ нестача вологи роговому шару шкіри.\n\n"
                              "Це тимчасовий стан і він досить легко коригується доглядом.", parse_mode='HTML')

    delete_message(chat_id, call.message.message_id)
    time.sleep(10)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Так", callback_data="dehydration_yes"),
        types.InlineKeyboardButton(text="Ні", callback_data="dehydration_no")]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Чи відчуваєте ви зневодненість?", reply_markup=keyboard)
    time.sleep(1)

@bot.callback_query_handler(func=lambda call: call.data == 'dehydration_yes' or call.data == 'dehydration_no')
def callback_query_skin_condition_dehydration(call):
    chat_id = call.message.chat.id
    if chat_id not in user_answers:
        user_answers[chat_id] = {}

    if call.data == 'dehydration_yes':
        user_answers[chat_id]["dehydration"] = "yes"
    else:
        user_answers[chat_id]["dehydration"] = "no"

    bot.send_message(chat_id, "<b>Ваша відповідь врахована ✅</b>\n\n"
                              "І ми досліджуємо далі)", parse_mode='HTML')
    time.sleep(1)
    delete_message(call.message.chat.id, call.message.message_id)
    time.sleep(1)
    bot.send_message(chat_id, "<b>Ми переходимо до зʼясування рівня чутливості 👼 Вашої шкіри.</b>\n\n"
                              "Це стан, який може бути набутим (наслідком впливу зовнішніх факторів).\n\n"
                              "Або ж вродженим (генетична особливість)", parse_mode='HTML')
    bot.send_message(chat_id, "Для визначення рівня чутливості Вам потрібно оцінити кожен пункт <b>за десятибальною шкалою</b>"
                              "(у разі, якщо відчуття нехарактерне, пункт оцінюється в 0 балів)👌", parse_mode='HTML')
    time.sleep(1)
    bot.send_message(chat_id, "Оцініть схильність Вашої шкіри до почервонінь", reply_markup=create_rating_keyboard("redness"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('redness_'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["redness"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Чи притаманне Вам відчуття тепла в шкірі? Яка інтенсивність?", reply_markup=create_rating_keyboard("heat_sensation"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('heat_sensation'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["heat_sensation"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "На скільки балів Ви б оцінили роздратування?", reply_markup=create_rating_keyboard("burning_sensation"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('burning_sensation'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["burning_sensation"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Чи відчуваєте Ви свербіж? Оцініть інтенсивність", reply_markup=create_rating_keyboard("itchiness"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('itchiness'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["itchiness"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Оцініть відчуття болю", reply_markup=create_rating_keyboard("pain"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pain'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["pain"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Яку б оцінку ви поставили загальному відчуттю дискомфорту?", reply_markup=create_rating_keyboard("discomfort"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('discomfort'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["discomfort"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Чи притаманне Вам відчуття приливів крові? Оцініть", reply_markup=create_rating_keyboard("blood_rush"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('blood_rush'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["blood_rush"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "Оцініть відчуття печіння", reply_markup=create_rating_keyboard("burning"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('burning'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["burning"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "На скільки балів Ви оціните поколювання Вашої шкіри, якщо таке відчуття присутнє?", reply_markup=create_rating_keyboard("stinging"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stinging'))
def callback_query_skin_redness(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["stinging"] = int(call.data.split('_')[-1])
    bot.send_message(chat_id, "У скільки балів Ви б оцінили відчуття стягнутості?", reply_markup=create_rating_keyboard("damag"))
    delete_message(chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('damag'))
def callback_query_skin_damag(call):
    chat_id = call.message.chat.id
    user_answers[chat_id]["damag"] = int(call.data.split('_')[-1])
    delete_message(chat_id, call.message.message_id)
    time.sleep(3)
    calculate_skin_condition(call.message)

def calculate_skin_condition(message):
    chat_id = message.chat.id
    if chat_id not in user_answers:
        return

    redness = user_answers[chat_id].get("redness", 0)
    heat_sensation = user_answers[chat_id].get("heat_sensation", 0)
    burning_sensation = user_answers[chat_id].get("burning_sensation", 0)
    itchiness = user_answers[chat_id].get("itchiness", 0)
    pain = user_answers[chat_id].get("pain", 0)
    discomfort = user_answers[chat_id].get("discomfort", 0)
    blood_rush = user_answers[chat_id].get("blood_rush", 0)
    burning = user_answers[chat_id].get("burning", 0)
    stinging = user_answers[chat_id].get("stinging", 0)
    damag = user_answers[chat_id].get("damag", 0)

    score = redness + heat_sensation + burning_sensation + itchiness + pain + discomfort + blood_rush + burning + stinging + damag

    skin_type = user_answers[chat_id].get("skin_type", "")
    dehydration = user_answers[chat_id].get("dehydration", "")

    if score <= 20:
        result = "нечутлива"
    elif 20 < score <= 60:
        result = "чутлива"
    else:
        result = "надто чутлива і потрібна обов'язково консультація лікаря"

    if skin_type == "dry":
        skin_type_text = "Сухий тип"
    elif skin_type == "normal":
        skin_type_text = "Нормальний тип"
    elif skin_type == "1":
        skin_type_text = "Жирний тип із жирною себореєю"
    elif skin_type == "2":
        skin_type_text = "Комбі/Жирний тип із сухою себореєю"
    elif skin_type == "3":
        skin_type_text = "Комбі/Жирний тип із змішаною себореєю"
    else:
        skin_type_text = skin_type

    if dehydration == "yes":
        dehydration_text = "Зневоднена"
    elif dehydration == "no":
        dehydration_text = "Не зневоднена"
    else:
        dehydration_text = ""

    user_answers[chat_id]["score"] = score
    user_answers[chat_id]["result"] = result
    user_answers[chat_id]["skin_type_text"] = skin_type_text
    user_answers[chat_id]["dehydration_text"] = dehydration_text

    bot.send_message(message.chat.id, "Вітаю 🎉\n" "Тест пройдено, а Ваші відповіді опрацьовуються\n\n"
                                      "Дякую за довіру 🤍", parse_mode='HTML')
    time.sleep(2)
    bot.send_message(message.chat.id, f"<b>У Вас</b> {skin_type_text} шкіри.\n"
                                      f"{dehydration_text}.\n"
                                      f"<b>За шкалою Мізері Ви отримали оцінку</b>: {score}.\n"
                                      f"І це свідчить про те, <b>що Ваша шкіра</b> {result}.", parse_mode='HTML')
    time.sleep(4)
    bot.send_message(chat_id, "Якщо бажаєте продовжити консультацію або виникли додаткові питання - натискайте на зручний спосіб зв'язку з нашим консультантом:", reply_markup=types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="Telegram", url="https://t.me/consultant_Limitless"),
        types.InlineKeyboardButton(text="Instagram", url="https://www.instagram.com/limitless.shop_/")))

    bot.send_message(chat_id, "Перейти на сайт магазину", reply_markup=types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="shop", url="https://limitlessua.com/")))
    time.sleep(4)
    bot.send_message(message.chat.id, "Не забувайте себе приймати, любити та турбуватись 🤍\n\n"
                                      "<b>Ваша краса</b>, неповторність та особливість <b>не має меж</b>\n\n"
                                      "<b>А ми</b> з радістю <b>допоможемо</b> Вам більш <b>розуміти</b> Вашу шкіру та <b>підбирати догляд</b> по потребах 🥰\n\n"
                                      "З любов'ю <b>Limitless</b> 🌱", parse_mode='HTML')
    send_results_to_admins(chat_id, message.chat.username, skin_type_text, dehydration_text, score, result)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Тиць', callback_data='button_pressed'))

    bot.send_message(message.chat.id, "Натисни якщо хочеш пройти знову", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'button_pressed':
        bot.send_message(call.message.chat.id, "/start")

def send_results_to_admins(chat_id, username, skin_type_text, dehydration_text, score, result):
    text = f"Результати тестування для користувача {username}:\n" \
           f"Тип шкіри: {skin_type_text}\n" \
           f"Стан зволоженості: {dehydration_text}\n" \
           f"Бали: {score}\n" \
           f"Результат: {result}"

    bot.send_message(1580990462, text)
    bot.send_message(5210739777, text)

users = {}

@bot.message_handler(commands=['post'])
def post_handler(message):
    if message.chat.id == 1580990462:
        text = message.text.replace('/post ', '', 1)
for user_id in users:
    try:
        bot.send_message(user_id, text)
    except Exception as e:
        print(f'Error sending message to {user_id}: {e}')

@bot.message_handler(commands=['post'])
def post_handler(message):
    if message.chat.id == 5210739777:
        text = message.text.replace('/post ', '', 1)
        for user_id in users:
            try:
                bot.send_message(user_id, text)
            except Exception as e:
                print(f'Error sending message to {user_id}: {e}')

ADMINS = ['1580990462', '5210739777']

def send_status_message():
    while True:
        for admin_id in ADMINS:
            try:
                bot.send_message(chat_id=admin_id, text="Я досі працюю!")
            except Exception as e:
                print(f"Помилка при надсиланні повідомлення адміністратору {admin_id}: {e}")
        time.sleep(7200)

print("Бот запущений...")
thread = Thread(target=send_status_message)
thread.start()
if __name__ == '__main__':
    print("Бот готовий до роботи. Надішліть команду /start для запуску.")
    bot.polling(none_stop=True)