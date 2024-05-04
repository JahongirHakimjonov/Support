import asyncio
import logging
import os
import time
from datetime import datetime

import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import (
    BotBlocked,
    ChatNotFound,
    UserDeactivated,
)
from aiogram.utils.exceptions import TelegramAPIError
from aiohttp.client_exceptions import ClientConnectorError
from dotenv import load_dotenv, find_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor

load_dotenv(find_dotenv("env/.env"))

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dbname = os.getenv("SQL_DATABASE")
user = os.getenv("SQL_USER")
password = os.getenv("SQL_PASSWORD")
host = os.getenv("SQL_HOST")

admin_ids_cache = []
group_ids_cache = []


def setup_database():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            cursor_factory=DictCursor,
        )
        cur = conn.cursor()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn, cur
    except psycopg2.OperationalError as e:
        logging.error(f"Error in database connection: {e}")
        exit(1)


conn, c = setup_database()


def get_admin_ids():
    c.execute("SELECT telegram_id FROM bot_users WHERE role = 'admin'")
    admin_ids = [row[0] for row in c.fetchall()]
    return admin_ids


def get_group_ids():
    c.execute("SELECT group_id FROM telegram_group_id")
    group_ids = [row[0] for row in c.fetchall()]
    return group_ids


async def update_admin_ids_cache():
    global admin_ids_cache
    admin_ids_cache = get_admin_ids()


async def update_group_ids_cache():
    global group_ids_cache
    group_ids_cache = get_group_ids()


async def schedule_cache_updates():
    while True:
        await update_admin_ids_cache()
        await update_group_ids_cache()
        await asyncio.sleep(3600)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    # Execute the query
    c.execute("SELECT * FROM bot_users WHERE telegram_id = %s", (user_id,))

    # Fetch the result
    user_exists = c.fetchone()

    # If user does not exist, insert their details into the database
    if not user_exists:
        c.execute(
            "INSERT INTO bot_users (first_name, last_name, username, telegram_id, created_at, updated_at, "
            "language_code, is_active, phone, role) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "
            "'uz', TRUE, 0, 'user')",
            (first_name, last_name, username, user_id),
        )
    else:
        # If user exists, update their details in the database
        c.execute(
            "UPDATE bot_users SET first_name = %s, last_name = %s, username = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE telegram_id = %s",
            (first_name, last_name, username, user_id),
        )

    conn.commit()
    keyboard = InlineKeyboardMarkup()
    button_website = InlineKeyboardButton(
        "Bizning kanalimiz", url="https://t.me/jakhangir_blog"
    )
    keyboard.add(button_website)

    if user_id in get_admin_ids():
        await message.reply(
            f"Salom Admin [{first_name}](tg://user?id={user_id})!\nbotga xush kelibsiz.",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    else:
        await message.reply(
            f"Salom [{first_name}](tg://user?id={user_id})! Talab va takliflaringiz bo‘lsa, ularni yuboring. \nBarcha gapingizni 1ta xabarda yozing.  "
            "\n\nDiqqat!, xabar faqat tekst ko‘rinishida bo‘lishi kerak. Rasm, video va boshqa formatdagi fayllar "
            "qabul qilinmaydi.",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )


class News(StatesGroup):
    waiting_for_news = State()


@dp.message_handler(commands=["news"])
async def send_news(message: types.Message):
    if message.from_user.id in get_admin_ids():
        await News.waiting_for_news.set()
        await message.reply(
            "Xabarni yuboring. Xabarni yuborishni bekor qilish uchun /cancel ni bosing."
        )
    else:
        await message.reply("Siz admin emassiz dib ettimu!!!")


# Respond to /news command
@dp.message_handler(state=News.waiting_for_news, content_types=types.ContentType.ANY)
async def handle_news(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await state.finish()
        await message.reply("Yangilik yuborish bekor qilindi")
    elif message.from_user.id in get_admin_ids():
        # Get all users from the database
        c.execute("SELECT telegram_id FROM bot_users WHERE telegram_id IS NOT NULL")
        users = c.fetchall()

        for user in users:
            telegram_id = user[0]
            try:
                if telegram_id in get_admin_ids():
                    continue
                await bot.copy_message(telegram_id, message.chat.id, message.message_id)
            except BotBlocked:
                logging.warning(f"Bot was blocked by the user {telegram_id}")
                continue
            except ChatNotFound:
                logging.warning(f"Chat not found for the user {telegram_id}")
            except UserDeactivated:
                logging.warning(f"User {telegram_id} is deactivated")
                continue

        await state.finish()

        for admin_id in get_admin_ids():
            try:
                await bot.send_message(admin_id, "Xabaringiz yuborildi.")
            except Exception as e:
                logging.error(
                    f"Error occurred while sending message to admin {admin_id}: {e}"
                )


# Respond to message
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    if message.from_user.id in admin_ids_cache:
        return

    for group_id in group_ids_cache:
        try:
            admins = await bot.get_chat_administrators(group_id)
            admin_ids = [admin.user.id for admin in admins]
            if message.from_user.id in admin_ids:
                return
        except ChatNotFound:
            logging.warning(f"Chat not found for the group {group_id}")

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    message_text = message.text

    # Check the count of messages for the current day
    c.execute(
        "SELECT message_count FROM daily_message WHERE telegram_id = %s AND message_date = CURRENT_DATE",
        (user_id,),
    )
    result = c.fetchone()

    if result is None:
        # This is the first message of the day, insert a new row

        c.execute(
            "INSERT INTO daily_message (telegram_id, message_date, message_count, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (
                message.from_user.id,
                datetime.now().date(),
                1,
                datetime.now(),
                datetime.now(),
            ),
        )
        conn.commit()
    elif result[0] < 10:
        # The user can still send messages today, increment the count
        c.execute(
            "UPDATE daily_message SET message_count = message_count + 1 WHERE telegram_id = %s AND message_date = "
            "CURRENT_DATE",
            (user_id,),
        )
        conn.commit()
    else:
        # The user has reached their daily limit
        await message.reply("Siz 1 kunda 10ta xabar yuborishingiz mumkin.")
        return

    # Create inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton(
        "Javob berish", callback_data=str(user_id)
    )  # Store user_id in callback_data
    keyboard.add(reply_button)

    try:
        # Send information to group with inline keyboard
        for group_id in get_group_ids():
            await bot.send_message(
                group_id,
                f"Foydalanuvchi: {user_name}\nId: {user_id}\nXabar: {message_text}",
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )
        await message.reply("Xabaringiz qabul qilindi. Javobni kuting.")
    except BotBlocked:
        logging.warning(f"Bot was blocked by the user {user_id}")
    except ChatNotFound:
        logging.warning(f"Chat not found for the user {user_id}")
    except UserDeactivated:
        logging.warning(f"User {user} is deactivated")
        for admin_id in get_admin_ids():
            await bot.send_message(admin_id, "Guruh topilmadi. Guruh ID ni tekshiring.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    user_id = int(callback_query.data)  # Retrieve user_id from callback_data

    # Get the list of administrators in the group
    group_ids = get_group_ids()
    admin_ids = []
    for group_id in group_ids:
        try:
            admins = await bot.get_chat_administrators(group_id)
            admin_ids.extend([admin.user.id for admin in admins])
        except ChatNotFound:
            logging.warning(f"Chat not found for the group {group_id}")

    # Check if the user who pressed the button is an admin
    if callback_query.from_user.id in admin_ids:
        await state.update_data(user_id=user_id)  # Store user_id
        logging.info(f"User_id: {user_id}")
        for group_id in get_group_ids():
            try:
                await bot.send_message(
                    group_id, "Javob matnini kiriting:"
                )  # Ask admin to reply
            except ChatNotFound:
                logging.warning(f"Chat not found for the group {group_id}")
            except Exception as e:
                logging.error(f"Error occurred: {e}")
        await state.set_state("admin_reply")
    else:
        for group_id in get_group_ids():
            try:
                await bot.send_message(group_id, "Siz admin emassiz.")
            except ChatNotFound:
                logging.warning(f"Chat not found for the group {group_id}")
            except Exception as e:
                logging.error(f"Error occurred: {e}")
        await state.finish()


@dp.message_handler(state="admin_reply", content_types=types.ContentType.ANY)
async def handle_admin_reply(message: types.Message, state: FSMContext):
    user_data = await state.get_data()  # Get user_id
    user_id = user_data.get("user_id")
    if user_id:
        try:
            # Check if the user has interacted with the bot
            c.execute("SELECT * FROM bot_users WHERE telegram_id = %s", (user_id,))
            user_exists = c.fetchall()
            if user_exists:
                await bot.copy_message(
                    user_id, message.chat.id, message.message_id
                )  # Send message to user
                for group_id in get_group_ids():
                    await bot.send_message(
                        group_id, "Javobingiz yuborildi."
                    )  # Send confirmation to admin
            else:
                for group_id in get_group_ids():
                    await bot.send_message(
                        group_id, "Foydalanuvchi bot bilan suhbatni boshlamagan."
                    )  # Notify admin
            await state.finish()  # Clear user_data
        except BotBlocked:
            logging.warning(f"Bot was blocked by the user {user_id}")
            for group_id in get_group_ids():
                await bot.send_message(group_id, "Foydalanuvchi botni blokladi.")
            await state.finish()
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            for group_id in get_group_ids():
                await bot.send_message(
                    group_id, f"Xatolik yuz berdi: {e}"
                )  # Send error message to admin
            await state.finish()
    else:
        for group_id in get_group_ids():
            await bot.send_message(
                group_id,
                "Xatolik: Foydalanuvchi topilmadi. Iltimos, qaytadan urinib ko'ring.",
            )
        await state.finish()


@dp.message_handler(commands=['about'])
async def about_command(message: types.Message):
    c.execute("SELECT * FROM about")
    about_info = c.fetchone()
    if about_info:
        about_message = f"Full Name: {about_info['full_name']}\n" \
                        f"Date: {about_info['date']}\n" \
                        f"Age: {about_info['age']}\n" \
                        f"Info: {about_info['info']}\n" \
                        f"Resume Link: {about_info['resume_link']}\n" \
                        f"Github Link: {about_info['github_link']}\n" \
                        f"Portfolio Link: {about_info['portfolio_link']}\n" \
                        f"Linkedin Link: {about_info['linkedin_link']}\n" \
                        f"Instagram Link: {about_info['instagram_link']}\n" \
                        f"Telegram Link: {about_info['telegram_link']}"

        # Send the message
        await bot.send_photo(chat_id=message.chat.id, photo=about_info['image'], caption=about_message,
                             parse_mode="Markdown")
    else:
        await bot.send_message(chat_id=message.chat.id, text="No information available.")


if __name__ == "__main__":
    retry_count = 5
    delay = 5
    for i in range(retry_count):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(schedule_cache_updates())  # Moved inside the main function
            executor.start_polling(dp, skip_updates=True)
            break
        except (TelegramAPIError, ClientConnectorError) as e:
            if i < retry_count - 1:  # If it's not the last attempt
                logging.error(f"Error occurred, retrying after {delay} seconds...")
                time.sleep(delay)  # Wait for some time before the next attempt
            else:
                logging.error(f"Failed to start polling after {retry_count} attempts.")
                raise e  # If all attempts failed, raise the exception
        except Exception as e:
            logging.error(f"Error occurred: {e}")
