import logging
import asyncio
from datetime import datetime, time, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from bot.routers.utils import read_employee_data, send_feedback_to_server, get_language_from_server
from bot.lang.kk import kk
from bot.lang.ru import ru
from aiogram.filters import StateFilter

logging.basicConfig(level=logging.INFO)

button_5_router = Router(name="button_5_router")
scheduler = AsyncIOScheduler()
storage = MemoryStorage()


class Day5States(StatesGroup):
    waiting_for_answer = State()


async def translate_message(user_lang: str, message_type: str) -> str:
    translations = {
        'kk': kk,
        'ru': ru
    }
    lang_translations = translations.get(user_lang, ru)
    message_text = lang_translations.get(message_type, message_type)
    logging.info(f"Translated '{message_type}' to '{message_text}' for language '{user_lang}'")
    return message_text


async def send_scheduled_message(bot: Bot, chat_id: int, message_text: str, keyboard=None):
    logging.info(f"Sending message to {chat_id}: {message_text}")
    await bot.send_message(chat_id, message_text, reply_markup=keyboard)


async def send_message_with_language(bot: Bot, chat_id: int, telegram_id: int, message_type: str, keyboard=None):
    user_lang = await get_language_from_server(telegram_id)
    message_text = await translate_message(user_lang, message_type)
    await send_scheduled_message(bot, chat_id, message_text, keyboard)


async def send_day5_sequence(bot: Bot, chat_id: int, telegram_id: int):
    await send_message_with_language(bot, chat_id, telegram_id, "day5_1")
    await asyncio.sleep(1)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await translate_message(await get_language_from_server(telegram_id), "1"), callback_data="day5_button1")],
        [InlineKeyboardButton(text=await translate_message(await get_language_from_server(telegram_id), "2"), callback_data="day5_button2")]
    ])
    await send_message_with_language(bot, chat_id, telegram_id, "day5_2", keyboard)


@button_5_router.callback_query(F.data == "day5_button1")
async def handle_day5_button1(callback: CallbackQuery):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(await translate_message(lang, "day5_button1"), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=await translate_message(lang, "lets_go"), callback_data="lets_go")]]
    ))


@button_5_router.callback_query(F.data == "lets_go")
async def handle_lets_go(callback: CallbackQuery):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(await translate_message(lang, "checklist"))
    await asyncio.sleep(1)
    await callback.message.answer(await translate_message(lang, "wishes"))


@button_5_router.callback_query(F.data == "day5_button2")
async def handle_day5_button2(callback: CallbackQuery):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(await translate_message(lang, "day5_button2"), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=await translate_message(lang, "answer"), callback_data="answer")]]
    ))


@button_5_router.callback_query(F.data == "answer")
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(await translate_message(lang, "please_write_suggestion"))
    await state.set_state(Day5States.waiting_for_answer)


@button_5_router.message(F.text, StateFilter(Day5States.waiting_for_answer))
async def handle_user_response(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    user_response = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, 'problems', user_response, current_time)
    lang = await get_language_from_server(user_id)
    await message.answer(await translate_message(lang, "thanks_day_5"), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=await translate_message(lang, "and"), callback_data="and")]]
    ))
    await state.clear()


@button_5_router.callback_query(F.data == "and")
async def handle_and(callback: CallbackQuery):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(text=await translate_message(lang, "check_day5"))
    await asyncio.sleep(1)
    await callback.message.answer(text=await translate_message(lang, "checklist"))
    await asyncio.sleep(1)
    await callback.message.answer(text=await translate_message(lang, "wishes"))


async def schedule_user_messages_5(bot: Bot):
    users = read_employee_data()
    for user in users:
        chat_id = user['telegram_id']
        telegram_id = user['telegram_id']
        first_day_str = user.get('first_day')
        role = user.get('role')

        if role not in ["security", "shop", "support", "office"]:
            continue

        if first_day_str is None:
            logging.warning(f"No first_day value for user '{telegram_id}'")
            continue

        try:
            first_day = datetime.strptime(first_day_str, '%Y-%m-%d').date()
        except ValueError as e:
            logging.error(f"Error converting first_day string to date for user '{telegram_id}': {e}")
            continue

        day5 = first_day + timedelta(days=4)
        scheduled_time = datetime.combine(day5, time(9, 0))
        if scheduled_time > datetime.now():
            key = f"{chat_id}_day5"
            scheduler.add_job(send_day5_sequence, DateTrigger(run_date=scheduled_time), args=[bot, chat_id, telegram_id], id=key, replace_existing=True)
            logging.info(f"Scheduled Day 5 messages for user '{telegram_id}' at {scheduled_time}")


def start_scheduler_5():
    scheduler.start()