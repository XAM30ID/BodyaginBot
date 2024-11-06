import sqlite3


def give_colors():
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    colors = cur.execute("""SELECT title FROM colors""").fetchall()
    con.close()
    return colors


def give_prints():
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    prnts = cur.execute("""SELECT title FROM prints""").fetchall()
    con.close()
    return prnts


def give_available_prints(color):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    available_prints = cur.execute(f"""SELECT prints FROM colors WHERE title = '{color}'""").fetchone()[0].split(";")
    con.close()
    if available_prints[0] == "*":
        available_prints = [elem[0] for elem in give_prints()]
    return available_prints


def give_available_colors(prnt):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    available_colors = cur.execute(f"""SELECT title, prints FROM colors""").fetchall()
    con.close()
    sp = []
    for color, prints in available_colors:
        if prints == "*":
            sp.append(color)
        elif prnt in prints.split(";"):
            sp.append(color)
    return sp


def add_user(chat_id, name, link):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO users(chat_id, name, link)
                VALUES ('{chat_id}', '{name}', '{link}')""")
    con.commit()
    con.close()


def user_regs(chat_id):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT chat_id FROM users WHERE chat_id = '{chat_id}'""").fetchone()
    con.close()
    return user is None


def give_user(chat_id):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT name, link FROM users WHERE chat_id = '{chat_id}'""").fetchone()
    con.close()
    return user


def add_goods(chat_id, order):
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT name, link, orders_count FROM users WHERE chat_id = '{chat_id}'""").fetchone()
    cur.execute(f"""INSERT INTO orders(user_name, user_link, order_text)
                VALUES ('{user[0]}', '{user[1]}', '{order}')""")

    cur.execute(f"""UPDATE users
                SET orders_count = {user[2] + 1}
                WHERE chat_id = '{chat_id}'""")

    con.commit()
    order_id = cur.execute(f"""SELECT id FROM orders""").fetchall()
    con.close()
    return order_id[-1][0]


def give_order(chat_id, order_id):
    if not order_id.isdigit():
        return 'Строка должна состоять из цифр'
    con = sqlite3.connect("main_BD.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT name FROM users WHERE chat_id = '{chat_id}'""").fetchone()
    order = cur.execute(f"""SELECT order_text, order_state FROM orders 
                        WHERE user_name = '{user[0]}' AND id = {order_id}""").fetchone()
    con.close()
    if order is None:
        return "Заказа с таким ID нет"
    else:
        order_text = order[0][order[0].find("</b>"):]
        order_text = order_text[order_text.find("<b>"):]
        order_state = order[1]
        return order_text, order_state
