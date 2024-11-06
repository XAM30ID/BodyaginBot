# Импорт библиотек
from aiogram import Bot, Dispatcher, executor, types

import logging

from sql_conn import *

# Уровень логирования
logging.basicConfig(level=logging.INFO)

# Бот и обработчик
bot = Bot(token="5152631822:AAGwokzR3fyyPd0hhCUQ3gXALp7llemdK8I")
db = Dispatcher(bot)

# Inline-клавиатуры и работа с ними
back_btn = types.InlineKeyboardButton("Назад", callback_data="Return")
reset_btn = types.InlineKeyboardButton("Сбросить", callback_data="Reset")
reset_t_btn = types.InlineKeyboardButton("Сбросить", callback_data="T_Reset")
home_btn = types.KeyboardButton("Вернуться ↩️")

# Клавиатура для статуса и ассортимента
action_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
assort_btn = types.KeyboardButton("Посмотреть ассортимент 🛒")
stat_btn = types.KeyboardButton("Узнать статус заказа 📄")
action_markup.add(assort_btn, stat_btn)

# Клавиатура для выбора типа одежды
type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
t_shirt_btn = types.KeyboardButton('Футболку 👕')
hoodie_btn = types.KeyboardButton("Худи 🥼")
type_markup.add(t_shirt_btn, hoodie_btn)

# Клавиатура для выбора варианта, как выбирать одежду (цвет или рисунок)
assort_markup = types.InlineKeyboardMarkup(row_width=1)
color_btn = types.InlineKeyboardButton("По цвету", callback_data="Color_choice")
print_btn = types.InlineKeyboardButton("По рисунку", callback_data="Print_choice")
assort_markup.add(color_btn, print_btn, back_btn)

# Клавиатура для выбора цвета
colors_markup = types.InlineKeyboardMarkup(row_width=1)
for color in give_colors():
    colors_markup.add(types.InlineKeyboardButton(color[0], callback_data="Chosen_color" + color[0]))
colors_markup.add(back_btn)

# Клавиатура для выбора принта
prints_markup = types.InlineKeyboardMarkup(row_width=1)
for prnt in give_prints():
    prints_markup.add(types.InlineKeyboardButton(prnt[0], callback_data="Chosen_print" + prnt[0]))
prints_markup.add(back_btn)

# Клавиатура выбора пола
sex_markup = types.InlineKeyboardMarkup(row_width=2)
male_btn = types.InlineKeyboardButton("Муж", callback_data="Choice_sex_male")
female_btn = types.InlineKeyboardButton("Жен", callback_data="Choice_sex_female")
sex_markup.row(male_btn, female_btn)
sex_markup.add(reset_btn)

# Клавиатура выбора размеров
size_markup = types.InlineKeyboardMarkup(row_width=1)
for size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
    size_markup.add(types.InlineKeyboardButton(size, callback_data=f"Choice_size_{size}"))
size_markup.add(reset_btn)

# Клавиатура добавления или отклонения товара в заказ
accept_reject_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
yes_btn = types.KeyboardButton("Да 👍")
no_btn = types.KeyboardButton("Нет 👎")
accept_reject_markup.add(yes_btn, no_btn)

# Клавиатура действий при выводе всего заказа
add_or_no_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
add_btn = types.KeyboardButton("Да ➕")
no_add_btn = types.KeyboardButton("Нет ➖")
del_goods = types.KeyboardButton("Очистить корзину 🗑")
add_or_no_markup.add(add_btn, no_add_btn, del_goods)

# Клавиатура оформления заказа
arrange_or_no_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
arrange_btn = types.KeyboardButton("Оформить ☑️")
drop_btn = types.KeyboardButton("Сбросить ❌")
arrange_or_no_markup.add(arrange_btn, drop_btn)

# Клавиатура выбора цвета футболок
black_white_markup = types.InlineKeyboardMarkup(row_width=1)
t_black_col = types.InlineKeyboardButton("Черного", callback_data="T_col_black")
t_white_col = types.InlineKeyboardButton("Белого", callback_data="T_col_white")
black_white_markup.add(t_black_col, t_white_col, back_btn)

# Клавиатура выбора пола для футболок
t_sex_markup = types.InlineKeyboardMarkup(row_width=2)  #
t_male_btn = types.InlineKeyboardButton("Муж", callback_data="T_Choice_sex_male")
t_female_btn = types.InlineKeyboardButton("Жен", callback_data="T_Choice_sex_female")
t_sex_markup.row(t_male_btn, t_female_btn)
t_sex_markup.add(reset_t_btn)

# Клавиатура выбора размера для футболок
t_size_markup = types.InlineKeyboardMarkup(row_width=1)  #
for size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
    t_size_markup.add(types.InlineKeyboardButton(size, callback_data=f"T_Choice_size_{size}"))
t_size_markup.add(reset_t_btn)

# Список клавиатур
inline_markups = (action_markup, assort_markup, colors_markup, prints_markup, type_markup)

# список сообщений от клавиатур
messages_dict = {'Приветствую! Меня зовут <b>Бодягин</b>, я бот, который поможет оформить заказ и посмотреть статус '
                 'заказа \nЧто вы хотите сделать:': 0,
                 'Как вы бы хотели выбрать худи:': 1,
                 'Какого цвета Вы хотите футболку?': 1,
                 'Список доступных цветов:'
                 '\n(Любое худи - 1600 рублей)': 2,
                 "Список животных:"
                 "\n(Любое худи - 1600 рублей)": 2}

messages_sp = list(messages_dict.values())

# Разные штучки
order = ''
user_name = False
order_knowledge = False
order_states = {-1: 'Отклонен',
                0: 'Ожидает решения',
                1: 'Собирается',
                2: 'Собран',
                3: 'Отправлен'}


# Проверка на модератора
def IS_MODER(message):
    if message.chat.id == 763283309:
        return True
    else:
        return False


# Команда старт
@db.message_handler(commands=["start"])
async def start(message):
    global user_name, order_knowledge
    order_knowledge = False
    await bot.send_message(message.chat.id, text='Приветствую! Меня зовут <b>Бодягин</b>, я бот, который поможет '
                                                 'оформить заказ и посмотреть статус заказа.', parse_mode="html")
    # Проверка, зарегистрирован ли пользователь
    if user_regs(message.chat.id):
        await bot.send_message(message.chat.id,
                               text='Для начала оставьте ссылку или номер телефона и Ваше имя через тире '
                                    'для дальнейшей связи с Вами. Если сообщение не будет соответствовать '
                                    'формату, администратор не сможет связаться с Вами.'
                                    '\nНапример: https://t.me/ИВАН_1999 - Иван')
        user_name = True
    else:
        await bot.send_message(message.chat.id, text='\nЧто вы хотите сделать: ',
                               reply_markup=inline_markups[0], parse_mode="html")


# Обработчик сообщений
@db.message_handler(content_types=types.ContentTypes.TEXT)
async def messages(message: types.Message):
    global order, user_name, order_knowledge
    print()
    if user_regs(message.chat.id):
        if user_name:  # Регистрация пользователя
            try:
                link = message.text.strip().split("-")[0]
                name = message.text.strip().split("-")[1]
                add_user(message.chat.id, name, link)
                user_name = False
                await bot.send_message(message.chat.id, text='\nЧто вы хотите сделать: ',
                                       reply_markup=inline_markups[0], parse_mode="html")
            except:
                await bot.send_message(message.chat.id, text='Ваше сообщение некорректное. Отправьте в соответствии '
                                                             'с примером: https://t.me/ИВАН_1999 - Иван')
        else:
            await bot.send_message(message.chat.id,
                                   text='Для начала оставьте ссылку или номер телефона и Ваше имя через тире '
                                        'для дальнейшей связи с Вами. Если сообщение не будет соответствовать '
                                        'формату, администратор не сможет связаться с Вами.'
                                        '\nНапример: https://t.me/ИВАН_1999 - Иван')
            user_name = True

    elif order_knowledge:
        res = give_order(message.chat.id, message.text)
        if len(res) == 2:
            txt = f'ЗАКАЗ:\n' \
                  f'{res[0]}' \
                  f'\n\nСтатус: {order_states[res[1]]}'
        else:
            txt = res
        await bot.send_message(message.chat.id, txt, parse_mode='html')
        order_knowledge = False

    else:
        if message.text == "Посмотреть ассортимент 🛒":  # Действия при выборе кнопки "Посмотреть ассортимент"
            await bot.send_message(chat_id=message.chat.id,
                                   text="Что Вы хотите посмотреть:",
                                   reply_markup=inline_markups[-1])
            order = f'<u>ЗАКАЗ</u>:\n\n Пользователь: <b>{give_user(message.chat.id)[0]} - ' \
                    f'{give_user(message.chat.id)[1]}</b>'

        elif message.text == 'Узнать статус заказа 📄':
            await bot.send_message(message.chat.id, text="Отправьте ID Вашего заказа", parse_mode="html")
            order_knowledge = True
        elif message.text == 'Худи 🥼':
            await bot.send_message(chat_id=message.chat.id,
                                   text="Как вы бы хотели выбрать худи:",
                                   reply_markup=inline_markups[1])

        elif message.text == 'Футболку 👕':
            await bot.send_message(message.chat.id, 'Какого цвета Вы хотите футболку?', reply_markup=black_white_markup)

        elif message.text == "Да 👍" and order != "":
            await bot.send_message(chat_id=message.chat.id,
                                   text="Хотите ли Вы добавить товаров?",
                                   reply_markup=add_or_no_markup)

        elif message.text == "Нет 👎" and order != "":
            if order.count("___________________________________") > 1:
                order = order[:order.rfind("___________________________________")]
                await bot.send_message(chat_id=message.chat.id,
                                       text="Хотите ли Вы добавить товаров?",
                                       reply_markup=add_or_no_markup)
            else:
                await bot.send_message(message.chat.id, text='\nЧто вы хотите сделать: ',
                                       reply_markup=inline_markups[0], parse_mode="html")
                order = f'<u>ЗАКАЗ</u>:\n\n Пользователь: <b>{give_user(message.chat.id)[0]} - ' \
                        f'{give_user(message.chat.id)[1]}</b>'
            print(order)

        elif message.text == "Да ➕" and order != "":
            await bot.send_message(chat_id=message.chat.id,
                                   text="Что Вы хотите посмотреть:",
                                   reply_markup=inline_markups[-1])

        elif message.text == "Нет ➖":
            goods = order[order.find("</b>"):]
            goods = goods[goods.find('<b>'):]
            await bot.send_message(message.chat.id, text=f'Ваши товары: \n{goods}', reply_markup=arrange_or_no_markup,
                                   parse_mode="html")

        elif message.text == 'Оформить ☑️':
            order_id = add_goods(message.chat.id, order)
            await bot.send_message(message.chat.id, text=f"ID Вашего заказа: <code>{order_id}</code>"
                                                         f"\nНе потеряйте и не забудьте его.", parse_mode="html")
            await bot.send_message(message.chat.id, text='\nЧто вы хотите сделать: ',
                                   reply_markup=inline_markups[0], parse_mode="html")

        elif message.text == "Очистить корзину 🗑" and order != "" or message.text == "Сбросить ❌" and order != "":
            order = f''
            await bot.send_message(message.chat.id, text="<b>КОРЗИНА ОЧИЩЕНА</b>", parse_mode="html")
            await bot.send_message(message.chat.id, text='\nЧто вы хотите сделать: ',
                                   reply_markup=inline_markups[0], parse_mode="html")

        else:
            await bot.send_sticker(message.chat.id,
                                   'CAACAgIAAxkBAAEEEFJiI82UlJrBsUJH5q8NGhVLqWVvfwACFwEAAiI3jgRnUn-Ie8Ns0CME')
            await bot.send_message(message.chat.id, text="Извините, я не понимаю этого(", reply_markup=action_markup,
                                   parse_mode="html")


# Работа клавиатуры под сообщением
@db.callback_query_handler()
async def callback_inline(call: types.CallbackQuery):
    global order
    if call.message:
        if call.data[0] == "T":
            call_data = call.data[2:]
            if call_data[:len('col_')] == "col_":
                color = call.data[len('T_col_'):]
                if color == "black":
                    col = "Чёрный"
                else:
                    col = "Белый"

                available_prints_markup = types.InlineKeyboardMarkup(row_width=1)
                for elem in give_available_prints(col):
                    available_prints_markup.add(types.InlineKeyboardButton(text=elem,
                                                                           callback_data=f"T_Chosen_col:{col};print:{elem}"))
                available_prints_markup.add(reset_t_btn)

                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f"Вы выбрали цвет: <b>{col}</b>"
                                                 f"\n\nВот принты:", parse_mode="html",
                                            reply_markup=available_prints_markup)

            elif call_data[:len("Chosen_col:")] == "Chosen_col:":
                col = call_data[len("Chosen_col:"):call_data.find(";")]
                prnt = call.data[call.data.rfind(":") + 1:]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f'Цвет: <b>{col}</b>.'
                                                 f'\n\nРисунок: <b>{prnt}</b>.'
                                                 f'\n\nУкажите Ваш пол:', parse_mode="html", reply_markup=t_sex_markup)

            elif call_data[:len("Choice_sex_")] == "Choice_sex_":
                if call_data[len("Choice_sex_"):] == "male":
                    sex = 'Мужской'
                else:
                    sex = 'Женский'
                mess = call.message.text.replace("\n\nУкажите Ваш пол:",
                                                 "").replace("Цвет: ",
                                                             "Цвет: <b>").replace(".",
                                                                                  "</b>.").replace("Рисунок: ",
                                                                                                   'Рисунок: <b>') + \
                       f'\n\nПол: <b>{sex}</b>.' \
                       f'\n\nУкажите Ваш размер:'
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=mess, parse_mode="html", reply_markup=t_size_markup)

            elif call_data[:len("Choice_size_")] == "Choice_size_":
                size = call_data[len('Choice_size_'):]
                mess = 'Ваш <u>заказ</u>: \n\n<b>Футболка</b>\n\n' + \
                       call.message.text.replace("\n\nУкажите Ваш размер:",
                                                 "").replace("Цвет: ",
                                                             "Цвет: <b>").replace(".",
                                                                                  "</b>.").replace("Рисунок: ",
                                                                                                   'Рисунок: <b>').replace(
                           "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>.\n\n<b>Всё верно?</b>'

                order += '\n___________________________________' \
                         '\n\n<b>Футболка</b>\n\n' + call.message.text.replace("\n\nУкажите Ваш размер:",
                                                                               "").replace("Цвет: ",
                                                                                           "Цвет: <b>").replace(".",
                                                                                                                "</b>.").replace(
                    "Рисунок: ",
                    'Рисунок: <b>').replace(
                    "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>'

                await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                photo = mess[mess.find('Рисунок: <b>') + len('Рисунок: <b>'):mess.find("\n\nПол: ") - len('</b>.')]
                try:
                    with open(f"static/img/{photo}.png", 'rb') as photo:
                        await bot.send_photo(chat_id=call.message.chat.id, photo=photo,
                                             caption=mess, parse_mode="html", reply_markup=accept_reject_markup)
                except:
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text='Не удалось открыть изображение')
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text=mess, parse_mode="html", reply_markup=accept_reject_markup)

            if call_data == "Reset":
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text='Какого цвета Вы хотите футболку?', reply_markup=black_white_markup)

        else:
            # Начальный выбор по цвету
            if call.data == "Color_choice":  # Действия при выборе кнопки "По цвету"
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="Список доступных цветов:"
                                                 "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[2])

            # Начальный выбор по принту
            elif call.data == 'Print_choice':  # Действия при выборе кнопки "По рисунку"
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="Список животных:"
                                                 "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[3])

            # Выведение выбранного цвета, принтов, доступных для цвета
            elif call.data[:len("Chosen_color")] == "Chosen_color":
                col = call.data[len("Chosen_color"):]

                available_prints_markup = types.InlineKeyboardMarkup(row_width=1)
                for elem in give_available_prints(col):
                    available_prints_markup.add(types.InlineKeyboardButton(text=elem,
                                                                           callback_data=f"Chosen_col:{col};print:{elem}"))
                available_prints_markup.add(reset_btn)

                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f"Вы выбрали цвет: <b>{col}</b>"
                                                 f"\n\nВот доступные принты:", parse_mode="html",
                                            reply_markup=available_prints_markup)

            # Выведение выбранного принта, доступных цветов
            elif call.data[:len("Chosen_print")] == "Chosen_print":
                prnt = call.data[len("Chosen_print"):]

                available_colors_markup = types.InlineKeyboardMarkup(row_width=1)
                for elem in give_available_colors(prnt):
                    available_colors_markup.add(types.InlineKeyboardButton(text=elem,
                                                                           callback_data=f"Chosen_col:{elem};print:{prnt}"))
                available_colors_markup.add(reset_btn)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f"Вы выбрали рисунок: <b>{prnt}</b>"
                                                 f"\n\nВот доступные принты:", parse_mode="html",
                                            reply_markup=available_colors_markup)

            # Выведение выбранных принта и цвета, выбор пола
            elif call.data[:len("Chosen_col:")] == "Chosen_col:":
                col = call.data[len("Chosen_col:"):call.data.find(";")]
                prnt = call.data[call.data.rfind(":") + 1:]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f'Цвет: <b>{col}</b>.'
                                                 f'\n\nРисунок: <b>{prnt}</b>.'
                                                 f'\n\nУкажите Ваш пол:', parse_mode="html", reply_markup=sex_markup)

            # Вывод +пол, выбор размера
            elif call.data[:len("Choice_sex_")] == "Choice_sex_":
                if call.data[len("Choice_sex_"):] == "male":
                    sex = 'Мужской'

                else:
                    sex = 'Женский'
                mess = call.message.text.replace("\n\nУкажите Ваш пол:",
                                                 "").replace("Цвет: ",
                                                             "Цвет: <b>").replace(".",
                                                                                  "</b>.").replace("Рисунок: ",
                                                                                                   'Рисунок: <b>') + \
                       f'\n\nПол: <b>{sex}</b>.' \
                       f'\n\nУкажите Ваш размер:'
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=mess, parse_mode="html", reply_markup=size_markup)

            # Вывод полного товара, подведение итогов
            elif call.data[:len("Choice_size_")] == "Choice_size_":
                size = call.data[len('Choice_size_'):]
                mess = 'Ваш <u>заказ</u>: \n\n<b>Худи</b>\n\n' + \
                       call.message.text.replace("\n\nУкажите Ваш размер:",
                                                 "").replace("Цвет: ",
                                                             "Цвет: <b>").replace(".",
                                                                                  "</b>.").replace("Рисунок: ",
                                                                                                   'Рисунок: <b>').replace(
                           "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>.\n\n<b>Всё верно?</b>'

                order += '\n___________________________________' \
                         '\n\n<b>Худи</b>\n\n' + call.message.text.replace("\n\nУкажите Ваш размер:",
                                                                           "").replace("Цвет: ",
                                                                                       "Цвет: <b>").replace(".",
                                                                                                            "</b>.").replace(
                    "Рисунок: ",
                    'Рисунок: <b>').replace(
                    "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>'

                await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                photo = mess[mess.find('Рисунок: <b>') + len('Рисунок: <b>'):mess.find("\n\nПол: ") - len('</b>.')]
                try:
                    with open(f"static/img/{photo}.png", 'rb') as photo:
                        await bot.send_photo(chat_id=call.message.chat.id, photo=photo,
                                             caption=mess, parse_mode="html", reply_markup=accept_reject_markup)
                except:
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text='Не удалось открыть изображение')
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text=mess, parse_mode="html", reply_markup=accept_reject_markup)

            elif call.data == 'Return':  # Возвращение обратно
                text = call.message.text
                mess_id = messages_dict[text]
                try:
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                text=list(messages_dict.keys())[mess_id - 1],
                                                reply_markup=inline_markups[mess_id - 1], parse_mode="html")
                except:
                    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text=list(messages_dict.keys())[mess_id - 1],
                                           reply_markup=inline_markups[mess_id - 1], parse_mode="html")

            elif call.data == "Reset":
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=list(messages_dict.keys())[1], reply_markup=inline_markups[1])

    await bot.answer_callback_query(callback_query_id=call.id)


if __name__ == '__main__':
    executor.start_polling(db, skip_updates=True)
