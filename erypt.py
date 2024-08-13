import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import asyncio

# Токен вашего бота
TOKEN = '7031454856:AAHiAfS-S1YaBK54ykY4UIoLe39UP37Fc7w'

# Установка соединения с базой данных
conn = sqlite3.connect('currency_exchange.db')
cursor = conn.cursor()

# Создание таблицы пользователей, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
''')
conn.commit()

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

import time

# Переменные для хранения текущего курса и времени последнего обновления курса
current_rate = 10.00  # По умолчанию 1 ERYPT = 10 рублей
last_rate_update = time.time()

# Функция для автоматического обновления курса каждый час
def update_rate():
    global current_rate, last_rate_update
    while True:
        time.sleep(30)  # 3600 секунд = 1 час
        current_rate += 1.2  # Увеличиваем курс на 10 копеек
        last_rate_update = time.time()

# Функция для автоматического обнуления курса каждые 24 часа
def reset_rate():
    global current_rate, last_rate_update
    while True:
        time.sleep(120)  # 86400 секунд = 24 часа
        current_rate = 10.00  # Возвращаем курс к начальному значению
        last_rate_update = time.time()
user_states = {}
CREATOR_ID = 6832231878
# Обработчик команды /output_money


# Обработчик команды /obnul_b для обнуления баланса пользователя
@dp.message_handler(commands=['obnul_b'])
async def reset_balance(message: types.Message):
    # Проверяем, что команду ввел создатель бота
    if message.from_user.id != 6832231878:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    try:
        # Разбиваем аргументы команды
        _, user_id = message.text.split()
        user_id = int(user_id)

        # Обновляем баланс пользователя
        cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
        conn.commit()

        await message.answer(f"Баланс пользователя с ID {user_id} успешно обнулен.")
    except (ValueError, IndexError):
        await message.answer("Некорректный формат команды. Используйте /obnul_b [ID_пользователя]")





# Обработчик команды /send для отправки валюты другому пользователю
@dp.message_handler(commands=['send'])
async def send_currency(message: types.Message):
    user_id = message.from_user.id

    try:
        # Разбиваем аргументы команды
        _, receiver_id, amount = message.text.split()
        receiver_id = int(receiver_id)
        amount = int(amount)

        # Проверяем, что сумма отправки неотрицательная
        if amount < 0:
            await message.answer("Неверная сумма для отправки.")
            return

        # Проверяем, что у пользователя достаточно средств
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        sender_balance = cursor.fetchone()
        if not sender_balance or sender_balance[0] < amount:
            await message.answer("У вас недостаточно средств для отправки.")
            return

        # Обновляем баланс отправителя
        cursor.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))

        # Обновляем баланс получателя
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (receiver_id,))
        cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, receiver_id))

        # Фиксируем изменения в базе данных
        conn.commit()

        await message.answer(f"Вы успешно отправили {amount} ERYPT пользователю с ID {receiver_id}.")
    except (ValueError, IndexError):
        await message.answer("Некорректный формат команды. Используйте /send [ID_получателя] [сумма]. ID получателя вы можете узнать, нажав /start в боте @getmyid_bot")





# Обработчик команды /buy для покупки валюты
@dp.message_handler(commands=['buy'])
async def buy_currency(message: types.Message):
    user_id = message.from_user.id

    try:
        # Разбиваем аргументы команды
        _, amount = message.text.split()
        amount = int(amount)

        # Проверяем, что сумма покупки неотрицательная
        if amount < 0:
            await message.answer("Неверная сумма для покупки.")
            return

        # Генерируем уникальный номер заказа
        order_id = random.randint(1000, 9999)

        # Создаем уникальную ссылку для оплаты
        payment_link = f"https://donationalerts.com/r/v1zerty1?alert=1&comment=eryt_purchase_{order_id}"

        # Создаем клавиатуру с кнопкой "Я оплатил"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Я оплатил, заявка на одобрение", callback_data=f"approve_{amount}"))

        # Отправляем сообщение с ссылкой и кнопкой
        await message.answer(f"Ваш заказ на покупку {amount} ERYPT принят. Оплатите его по ссылке: {payment_link}",
                             reply_markup=keyboard)


    except (ValueError, IndexError):
        await message.answer("Некорректный формат команды. Используйте /buy [сумма]")


# Обработчик команды /add_b для добавления средств на баланс 

# Обработчик команды /help для вывода списка доступных команд
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = ("Список доступных команд:\n"
                 "/start - начать диалог\n"
                 "/balance - проверить баланс\n"
                 "/send [ID_получателя] [сумма] - отправить валюту\n"
                 "/buy [сумма] - купить валюту\n"
                 "/curs - Узнать курс ERYPT (Сколько стоит 1 ERYPT.)")
    # Добавляем команду обнуления баланса, если пользователь - создатель бота
    if message.from_user.id == 6832231878:
        help_text += "/obnul_b [ID_пользователя] - обнулить баланс пользователя\n"
    if message.from_user.id == 6832231878:
        help_text +="/add_b [ID] - Добавить баланс пользователю.\n"
    if message.from_user.id == 6832231878:
        help_text += "/obnul_curs [СУММА] - Обнулить курс.\n"

    await message.answer(help_text)

# Обработчик команды /add_b для добавления средств на баланс пользователя
@dp.message_handler(commands=['add_b'])
async def add_balance(message: types.Message):
    # Проверяем, что команду ввел создатель бота
    if message.from_user.id != 6832231878:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    try:
        # Разбиваем аргументы команды
        command_parts = message.text.split()
        if len(command_parts) != 3:
            raise ValueError("Некорректный формат команды.")

        _, user_id, amount = command_parts
        user_id = int(user_id)
        amount = int(amount)

        # Проверяем, что сумма для добавления неотрицательная
        if amount < 0:
            await message.answer("Неверная сумма для добавления.")
            return

        # Обновляем баланс пользователя
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        conn.commit()

        # Получаем юзернейм модератора
        moderator_username = message.from_user.username

        # Отправляем уведомление пользователю о пополнении баланса
        await bot.send_message(user_id, f"✅ Пополнение баланса на сумму: {amount} ERYPT. Модератор: @{moderator_username}")

        await message.answer(f"Баланс пользователя с ID {user_id} успешно пополнен на {amount} ERYPT. "
                             f"Модератор: @{moderator_username}")
    except (ValueError, IndexError):
        await message.answer("Некорректный формат команды. Используйте /add_b [ID_пользователя] [сумма]")



# Обработчик команды /add_money для добавления средств на баланс пользователя
@dp.message_handler(commands=['add_money'])
async def add_money(message: types.Message):
    # Проверяем, что команду ввел создатель бота
    if message.from_user.id != 6832231878:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    try:
        # Разбиваем аргументы команды
        _, user_id, amount = message.text.split()
        user_id = int(user_id)
        amount = int(amount)

        # Проверяем, что сумма для добавления неотрицательная
        if amount < 0:
            await message.answer("Неверная сумма для добавления.")
            return

        # Обновляем баланс пользователя
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        conn.commit()

        # Получаем юзернейм модератора
        moderator_username = message.from_user.username

        # Отправляем уведомление пользователю о пополнении баланса
        await bot.send_message(user_id, f"✅ Пополнение баланса на сумму: {amount} ERYPT. Модератор: @{moderator_username}")

        await message.answer(f"Баланс пользователя с ID {user_id} успешно пополнен на {amount} ERYT. "
                             f"Модератор: @{moderator_username}")
    except (ValueError, IndexError):
        await message.answer("Некорректный формат команды. Используйте /add_money [ID_пользователя] [сумма]")


# Обработчик команды /curs для отображения текущего курса
@dp.message_handler(commands=['curs'])
async def show_rate(message: types.Message):
    global current_rate
    await message.answer(f"Текущий курс: 1 ERYPT = 1 рубль ≈ 0.011 $")

# Обработчик команды /obnul_curs для сброса курса (только для создателя бота)
@dp.message_handler(commands=['obnul_curs'])
async def reset_rate_command(message: types.Message):
    if message.from_user.id != 6832231878:  # ID создателя бота
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    
    try:
        _, new_rate = message.text.split()
        new_rate = float(new_rate)
        global current_rate
        current_rate = new_rate
        await message.answer(f"Курс успешно сброшен на {new_rate} рублей.")
    except ValueError:
        await message.answer("Некорректный формат команды. Используйте /obnul_curs [новый_курс]")

# Добавляем выполнение функций обновления и сброса курса в блоке __main__
if __name__ == '__main__':
    # Запускаем новые потоки для обновления и сброса курса
    import threading
    threading.Thread(target=update_rate, daemon=True).start()
    threading.Thread(target=reset_rate, daemon=True).start()






# Обработчик команды /balance
@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, есть ли запись о пользователе в базе данных
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    # Если запись отсутствует, добавляем пользователя с нулевым балансом
    if not result:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        conn.commit()

    # Получение баланса пользователя из базы данных
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance_amount = cursor.fetchone()[0]
    
    await message.answer(f"Ваш текущий баланс: {balance_amount} ERYPT")

import os

# Получаем текущую директорию
current_dir = os.path.dirname(os.path.abspath(__file__))


# Полный путь к файлу ghh.txt
file_path = "/storage/emulated/0/Download/base_d.txt"
# Список для хранения ID уже обработанных пользователей
processed_users = []

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Добро пожаловать в обменник валюты ERYT (ейфрит)!\n"
                         "У вас на счету 0 ERYPT. Вы можете отправлять, получать и покупать валюту. Введите /help , чтобы узнать список команд.")
    
    # Отправляем уведомление о новом пользователе создателю бота
    if message.from_user.username and message.from_user.id != 6832231878:  # Проверяем, есть ли у пользователя юзернейм
        username = message.from_user.username
        
        # Проверяем, нет ли уже такого пользователя в базе данных
        if message.from_user.id not in processed_users:
            with open(file_path, "r") as file:
                for line in file:
                    if username in line:
                        processed_users.append(message.from_user.id)
                        return  # Если пользователь уже есть в файле, прерываем обработку
            # Если пользователь не найден в файле, добавляем его
            with open(file_path, "a") as file:
                file.write(f"ПОЛЬЗОВАТЕЛЬ @{username}, {message.from_user.id}\n")
                
            await bot.send_message(6832231878, f"✅ НОВЫЙ ПОЛЬЗОВАТЕЛЬ! @{username}")
            processed_users.append(message.from_user.id)




# Обработчик команды /clear_d для очистки базы данных (только для создателя бота)
@dp.message_handler(commands=['clear_d'])
async def clear_database(message: types.Message):
    if message.from_user.id != 6832231878:  # ID создателя бота
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    
    # Очищаем файл
    open(file_path, "w").close()
    
    await message.answer("База данных очищена.")

# Обработчик неизвестных кома


# Обработчик комнды /clear_d для очистки базы данных (только для создателя бота)
@dp.message_handler(commands=['clear_d'])
async def clear_database(message: types.Message):
    if message.from_user.id != 6832231878:  # ID создателя бота
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    
    # Очищаем базу данных
    cursor.execute("DELETE FROM users")
    conn.commit()
    
    # Очищаем файл
    open(file_path, "w").close()
    
    await message.answer("База данных очищена. Все пользователи удалены, балансы сброшены.")

# Обработчик команды /clear_d для очистки базы данных (только для создателя бота)
@dp.message_handler(commands=['clear_d'])
async def clear_database(message: types.Message):
    if message.from_user.id != 6832231878:  # ID создателя бота
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    
    # Очищаем базу данных
    cursor.execute("DELETE FROM users")
    conn.commit()
    
    await message.answer("База данных очищена. Все пользователи удалены, балансы сброшены.")



# Обработчик инлайн-кнопки "Я оплатил"
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('approve_'))
async def approve_payment(callback_query: types.CallbackQuery):
    try:
        # Получаем сумму из данных коллбэка
        amount = int(callback_query.data.split('_')[1])

        # Создаем клавиатуру с кнопками "✅ Одобрить" и "⛔ Отказ"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_yes_{amount}"),
                     InlineKeyboardButton("⛔ Отказ", callback_data=f"approve_no_{amount}"))

        # Отправляем уведомление создателю бота о заявке на одобрение
        await bot.send_message(6832231878, f"Новая заявка на: {amount} ERYPT.\n"
                                           f"Пользователь: @{callback_query.from_user.username}",
                               reply_markup=keyboard)

        # Отправляем уведомление пользователю о том, что заявка отправлена на одобрение
        await bot.send_message(callback_query.from_user.id, f"Заявка на пополнение баланса на {amount} ERYPT "
                                                             f"отправлена на одобрение.")

    except (ValueError, IndexError):
        await bot.send_message(callback_query.from_user.id, "Произошла ошибка при обработке вашего запроса.")



# Обработчик инлайн-кнопок "✅ Одобрить" и "⛔ Отказ" для создателя бота
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('approve_yes_') or
                                                     callback_query.data.startswith('approve_no_'))
async def process_approval(callback_query: types.CallbackQuery):
    try:
        # Получаем сумму из данных коллбэка
        data = callback_query.data.split('_')
        amount = int(data[2])
        user_id = callback_query.from_user.id

        # Обработка нажатия кнопки "✅ Одобрить"
        if data[1] == 'yes':
            # Обновляем баланс пользователя
            cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
            conn.commit()
            await bot.send_message(user_id, f"Заявка на пополнение баланса на {amount} ERYPT одобрена.")

        # Обработка нажатия кнопки "⛔ Отказ"
        elif data[1] == 'no':
            await bot.send_message(user_id, f"Заявка на пополнение баланса на {amount} ERYPT отклонена.")

        # Отправляем сообщение об успешной обработке запроса
        await bot.answer_callback_query(callback_query.id, "Запрос обработан успешно.")

    except (ValueError, IndexError):
        await bot.send_message(callback_query.from_user.id, "Произошла ошибка при обработке вашего запроса.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
