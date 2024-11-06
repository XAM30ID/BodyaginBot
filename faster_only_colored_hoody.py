# Импорт библиотек
from aiogram import Bot, Dispatcher, executor, types

import logging

from sql_conn_only_colored_hoody import *

# Уровень логирования
logging.basicConfig(level=logging.INFO)

# Бот и обработчик
bot = Bot(token="5152631822:AAGwokzR3fyyPd0hhCUQ3gXALp7llemdK8I")
db = Dispatcher(bot)

# Разные штучки
order = ''
user_name = False
order_knowledge = False
order_states = {-1: 'Отклонен',
                0: 'Ожидает решения',
                1: 'Собирается',
                2: 'Собран',
                3: 'Отправлен',
                4: 'Доставлен и получен'}

# Inline-клавиатуры и работа с ними
back_btn = types.InlineKeyboardButton("Назад", callback_data="Return")
reset_btn = types.InlineKeyboardButton("Сбросить", callback_data="Reset")
home_btn = types.KeyboardButton("Вернуться ↩️")

# Клавиатура для статуса и ассортимента
action_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
assort_btn = types.KeyboardButton("Посмотреть ассортимент 🛒")
stat_btn = types.KeyboardButton("Узнать статус заказа 📄")
action_markup.add(assort_btn, stat_btn)

# Клавиатура для выбора цвета
colors_markup = types.InlineKeyboardMarkup(row_width=1)
for color in give_colors():
    colors_markup.add(types.InlineKeyboardButton(color[0], callback_data="Chosen_color" + color[0]))
colors_markup.add(back_btn)

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

inline_markups = (action_markup, colors_markup)

MODER_main_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
orders_check = types.KeyboardButton('Список всех заказов 📃')
users_check = types.KeyboardButton('Список всех пользователей 👥')
MODER_main_markup.add(orders_check, users_check)

order_states_markup = types.InlineKeyboardMarkup(row_width=1)
for key, value in order_states.items():
    order_states_markup.add(types.InlineKeyboardButton(text=value, callback_data=f'restate_{key}'))


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

    if IS_MODER(message):
        await bot.send_message(message.chat.id, text='Приветствую, модератор! \nЧто ты хочешь сделать?',
                               parse_mode="html", reply_markup=MODER_main_markup)
    else:
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
    if not IS_MODER(message):
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
                                            text="Список доступных цветов:"
                                                 "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[1])
                order = f'<u>ЗАКАЗ</u>:\n\n Пользователь: <b>{give_user(message.chat.id)[0]} - ' \
                        f'{give_user(message.chat.id)[1]}</b>'

            elif message.text == 'Узнать статус заказа 📄':
                await bot.send_message(message.chat.id, text="Отправьте ID Вашего заказа", parse_mode="html")
                order_knowledge = True

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
                    await bot.send_message(chat_id=message.chat.id,
                                                text="Список доступных цветов:"
                                                     "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[1])

                    order = f'<u>ЗАКАЗ</u>:\n\n Пользователь: <b>{give_user(message.chat.id)[0]} - ' \
                            f'{give_user(message.chat.id)[1]}</b>'

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
                await bot.send_message(763283309, '<b>НОВЫЙ ЗАКАЗ</b>'
                                                  '\n\n' + order, parse_mode='html')

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

    else:
        if message.text == 'Список всех пользователей 👥':
            for user in give_all_users():
                await bot.send_message(message.chat.id, f"Пользователь: <b>{user[0]}</b>"
                                                        f"\nСвязь: <code>{user[1]}</code>"
                                                        f"\nКоличество заказов: <b>{user[2]}</b>", parse_mode='html')

        elif message.text == "Список всех заказов 📃":
            for order in give_all_orders():
                await bot.send_message(message.chat.id, f'ЗАКАЗ{order[3][order[3].find("/b>") + 3:]}'
                                                        f'\n\n\nid заказа: <b>{order[0]}</b>'
                                                        f'\n\n\nИмя пользователя: <b>{order[1]}</b>'
                                                        f'\n\n\nСвязь с пользователем: <code>{order[2]}</code>'
                                                        f'\n\n\nСтатус заказа: <b>{order_states[int(order[4])]}</b>',
                                       reply_markup=order_states_markup, parse_mode='html')



# Работа клавиатуры под сообщением
@db.callback_query_handler()
async def callback_inline(call: types.CallbackQuery):
    global order
    if call.message:
        # Начальный выбор по цвету
        if call.data == "Color_choice":  # Действия при выборе кнопки "По цвету"
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Список доступных цветов:"
                                             "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[2])

        # Выведение выбранного цвета, принтов, доступных для цвета
        elif call.data[:len("Chosen_color")] == "Chosen_color":
            col = call.data[len("Chosen_color"):]
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'Цвет: <b>{col}</b>.'
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
                                                                              "</b>.") + \
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
                                                                              "</b>.").replace(
                       "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>.\n\n<b>Всё верно?</b>'

            order += '\n___________________________________' \
                     '\n\n<b>Худи</b>\n\n' + call.message.text.replace("\n\nУкажите Ваш размер:",
                                                                       "").replace("Цвет: ",
                                                                                   "Цвет: <b>").replace(".",
                                                                                                        "</b>.").replace(
                "\n\nПол: ", "\n\nПол: <b>") + f'\n\nРазмер: <b>{size}</b>'

            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=mess, parse_mode="html", reply_markup=accept_reject_markup)

        elif call.data == 'Return':  # Возвращение обратно
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            order = f''
            await bot.send_message(call.message.chat.id, text='\nЧто вы хотите сделать: ',
                                   reply_markup=inline_markups[0], parse_mode="html")

        elif call.data == "Reset":
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Список доступных цветов:"
                                             "\n(Любое худи - 1600 рублей)", reply_markup=inline_markups[1])

        elif call.data[:len('restate_/')] == 'restate_':
            order_id = call.message.text
            print(order_id)

    await bot.answer_callback_query(callback_query_id=call.id)


if __name__ == '__main__':
    executor.start_polling(db, skip_updates=True)
