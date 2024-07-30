import logging
from datetime import datetime, timedelta, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.routers.utils import read_employee_data, send_feedback_to_server, get_language_from_server
from bot.lang import translate
from aiogram.filters import StateFilter

logging.basicConfig(level=logging.INFO)

class Day45FeedbackStates(StatesGroup):
    awaiting_suggestion_45 = State()
    awaiting_suggestion_45_2 = State()

feedback_45_router = Router(name="feedback_45_router")
scheduler = AsyncIOScheduler()

async def send_scheduled_message_45(bot: Bot, chat_id, text_message, keyboard=None):
    logging.info(f"Sending message to {chat_id}: {text_message}")
    await bot.send_message(chat_id, text_message, reply_markup=keyboard)

async def dispatch_message_45(bot: Bot, chat_id, username, message_type):
    users = read_employee_data()
    user = next((user for user in users if user['name'] == username), None)
    if user and user['role'] == 'shop':
        try:
            user_lang = await get_language_from_server(user['telegram_id'])
        except Exception as e:
            logging.error(f"Error fetching language from server for user {username}: {e}")
            user_lang = user.get('language', 'ru')

        text_template = translate(user_lang, message_type)
        message_text = text_template.format(name=username)

        if message_type == 'day14_first':
            keyboard = None
        elif message_type == 'day14_second':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day14_button_1")],
                [InlineKeyboardButton(text="2", callback_data="day14_button_2")],
                [InlineKeyboardButton(text="3", callback_data="day14_button_3")],
                [InlineKeyboardButton(text="4", callback_data="day14_button_4")]
            ])
        else:
            keyboard = None

        await send_scheduled_message_45(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")


def schedule_day45_messages(bot: Bot):
    users = read_employee_data()
    for user in users:
        chat_id = user['telegram_id']
        username = user['name']
        first_day_str = user.get('first_day')

        if first_day_str is None:
            logging.warning(f"No first_day value for user {username}")
            continue

        try:
            first_day = datetime.strptime(first_day_str, '%Y-%m-%d').date()
        except ValueError as e:
            logging.error(f"Error converting first_day string to date for user {username}: {e}")
            continue

        day45_date = first_day + timedelta(days=44)

        times = {
            'day14_first': time(17, 0),
            'day14_second': time(17, 0, 5),
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(day45_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(dispatch_message_45, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@feedback_45_router.callback_query(F.data.in_({"day14_button_1", "day14_button_2", "day14_button_3", "day14_button_4"}))
async def handle_day45_buttons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    message_type = callback.data
    try:
        lang = await get_language_from_server(user_id)
    except Exception as e:
        logging.error(f"Error fetching language from server for user {username}: {e}")
        lang = 'ru'

    if message_type in {"day14_button_1", "day14_button_2"}:
        response_message = translate(lang, 'day14_button1_2')
        await callback.message.edit_text(response_message)
    elif message_type == "day14_button_3":
        response_message = translate(lang, 'day14_button3')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day14_suggestion_reply")]
        ])
        await callback.message.edit_text(response_message, reply_markup=keyboard)
        await state.set_state(Day45FeedbackStates.awaiting_suggestion)
    elif message_type == "day14_button_4":
        response_message = translate(lang, 'day14_button4')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day14_suggestion_reply_4")]
        ])
        await callback.message.edit_text(response_message, reply_markup=keyboard)
        await state.set_state(Day45FeedbackStates.awaiting_suggestion_4)

    feedback = callback.data.split('_')[-1]
    send_feedback_to_server(username, user_id, "1.Мне комфортно😊\n2.Я чувствую себя увереннее😏\n3.У меня не все получается🦾\n4.Слишком много всего, я устаю😣", feedback, datetime.now().isoformat())


@feedback_45_router.callback_query(F.data == "day45_suggestion_reply")
async def handle_suggestion_reply_45(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(Day45FeedbackStates.awaiting_suggestion)


@feedback_45_router.callback_query(F.data == "day45_suggestion_reply_4")
async def handle_suggestion_reply_45_2(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(Day45FeedbackStates.awaiting_suggestion_4)


@feedback_45_router.message(F.text, StateFilter(Day45FeedbackStates.awaiting_suggestion_45))
async def handle_suggestion_response_45(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, "Problem of 45th day", suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day14_thanks')
    await message.answer(thanks_message)
    await state.clear()


@feedback_45_router.message(F.text, StateFilter(Day45FeedbackStates.awaiting_suggestion_45_2))
async def handle_suggestion_response_45_2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, "Problem of 45th day", suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day14_thanks')
    await message.answer(thanks_message)
    await state.clear()

def start_scheduling_45():
    scheduler.start()