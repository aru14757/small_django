from bot.routers.useful_info import useful_info
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import asyncio
from datetime import datetime, time, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.routers.utils import read_employee_data, send_feedback_to_server, get_language_from_server
from bot.lang.kk import kk
from bot.lang.ru import ru
from bot.lang import translate
from aiogram.filters import StateFilter

logging.basicConfig(level=logging.INFO)


class NewSuggestionStates(StatesGroup):
    waiting_for_feedback = State()


button_router = Router(name="button_router")
scheduler = AsyncIOScheduler()


async def schedule_message(bot: Bot, chat_id: int, text_message: str, keyboard=None):
    logging.info(f"Sending message to {chat_id}: {text_message}")
    await bot.send_message(chat_id, text_message, reply_markup=keyboard)


async def prepare_message(bot: Bot, chat_id: int, username: str, message_type: str):
    users = read_employee_data()
    user = next((user for user in users if user['name'] == username), None)

    if user and user['role'] == 'shop':
        user_lang = await get_language_from_server(user['telegram_id'])
        text_template = kk[message_type] if user_lang == 'kk' else ru[message_type]
        message_text = text_template.format(name=username)

        keyboard = None
        if message_type == 'day27_how':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="😊", callback_data="good_27")],
                [InlineKeyboardButton(text="😐", callback_data="normal_27")],
                [InlineKeyboardButton(text="😞", callback_data="bad_27")]
            ])
        elif message_type == 'day27_help':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "day27_help_button"), callback_data="useful_info")]
            ])
        elif message_type == 'giving_rate':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="rating_1")],
                [InlineKeyboardButton(text="2", callback_data="rating_2")],
                [InlineKeyboardButton(text="3", callback_data="rating_3")],
                [InlineKeyboardButton(text="4", callback_data="rating_4")],
                [InlineKeyboardButton(text="5", callback_data="rating_5")]
            ])
        elif message_type == 'day27_3_buttons':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="reply_suggestion")]
            ])

        await schedule_message(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")



def set_message_schedule(bot: Bot):
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

        day27_date = first_day + timedelta(days=26)

        times = {
            'day27_help': time(7, 30),
            'day27_how': time(20, 00),
            'giving_rate': time(20, 00)
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(day27_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


# Обработчик нажатия на кнопки с эмодзи
@button_router.callback_query(F.data.in_({"good_27", "normal_27", "bad_27"}))
async def process_smile_buttons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)  # Fetch language from server
    feedback = callback.data
    thanks_message = translate(lang, 'day27_thanks')
    await callback.message.answer(thanks_message)

    username = callback.from_user.username
    message_type = 'Как проходит 27 рабочий день?'
    current_time = datetime.now().isoformat()  # Текущее время в формате ISO 8601

    send_feedback_to_server(username, user_id, message_type, feedback, current_time)


@button_router.callback_query(F.data.in_({"rating_1", "rating_2", "rating_3", "rating_4", "rating_5"}))
async def process_rating_buttons(callback: CallbackQuery, state: FSMContext):
    rating_value = callback.data.split('_')[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    message_type = 'Оценка бота 27'
    current_time = datetime.now().isoformat()  # Текущее время в формате ISO 8601

    send_feedback_to_server(username, user_id, message_type, rating_value, current_time)

    await asyncio.sleep(1)
    lang = await get_language_from_server(user_id)  # Fetch language from server
    feedback_message = translate(lang, 'day27_3_buttons')
    await callback.message.answer(
        feedback_message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="reply_suggestion")]
            ]
        )
    )


@button_router.callback_query(F.data == "reply_suggestion")
async def process_reply_suggestion(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)  # Fetch language from server
    await callback.message.answer(translate(lang, 'day27_3_buttons'))
    await state.set_state(NewSuggestionStates.waiting_for_feedback)  # Устанавливаем состояние ожидания сообщения


@button_router.message(F.text, StateFilter(NewSuggestionStates.waiting_for_feedback))
async def process_suggestion_response(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Предложение по доработке бота"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day27_3_thanks')
    await message.answer(thanks_message)
    await state.clear()


@button_router.callback_query(F.data == "useful_info")
async def process_useful_info(callback: CallbackQuery, state: FSMContext):
    await useful_info(callback, state)


def start_scheduling():
    scheduler.start()