from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import logging
import asyncio
from datetime import datetime, time, timedelta
from bot.routers.utils import read_employee_data, send_feedback_to_server, get_language_from_server
from bot.lang.kk import kk
from bot.lang.ru import ru
from bot.lang import translate
from aiogram.filters import StateFilter

logging.basicConfig(level=logging.INFO)


class NewMessageStates_91(StatesGroup):
    waiting_for_feedback_day91_4_no = State()
    waiting_for_feedback_day91_5_no = State()
    waiting_for_feedback_day91_ev_91 = State()
    waiting_for_feedback_day91_5_yes = State()
    waiting_for_feedback_day91_6 = State()

button91_router = Router(name="button91_router")
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
        if message_type == 'day91_4':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day91_4_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day91_4_no")]
            ])
        elif message_type == 'day91_4_no':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day91_4_no_answer")]
            ])
        elif message_type == 'day91_5':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day91_5_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day91_5_no")]
            ])
        elif message_type == 'day91_6':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day91_6_answer")]
            ])
        elif message_type == 'day91_evening_message':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="evening_1")],
                [InlineKeyboardButton(text="2", callback_data="evening_2")],
                [InlineKeyboardButton(text="3", callback_data="evening_3")],
                [InlineKeyboardButton(text="4", callback_data="evening_4")],
                [InlineKeyboardButton(text="5", callback_data="evening_5")]
            ])
        elif message_type == 'day91_evening_message_2':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="reply_suggestion_91")]
            ])
        await schedule_message(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")


def set_message_schedule_91(bot: Bot):
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

        day91_date = first_day + timedelta(days=90)

        morning_times = {
            'day91_1': time(10, 0),
            'day91_2': time(10, 0, 1),
            'day91_3': time(10, 0, 2),
            'day91_4': time(14, 0)
        }

        evening_time = {
            'day91_evening_message': time(17,0)
        }

        for message_type, send_time in morning_times.items():
            scheduled_time = datetime.combine(day91_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])

        for message_type, send_time in evening_time.items():
            scheduled_time = datetime.combine(day91_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@button91_router.callback_query(F.data == "day91_4_yes")
async def handle_day91_4_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day91_4_yes'))
    await asyncio.sleep(1)
    await callback.message.answer(translate(lang, 'day91_5'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day91_5_yes")],
                                      [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day91_5_no")]
                                  ]))
    await callback.answer()


@button91_router.callback_query(F.data == "day91_4_no")
async def handle_day91_4_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day91_4_no'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day91_4_no_answer")]
                                  ]))
    await callback.answer()


@button91_router.callback_query(F.data == "day91_4_no_answer")
async def handle_day91_4_no_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_91.waiting_for_feedback_day91_4_no)
    await callback.answer()


@button91_router.message(StateFilter(NewMessageStates_91.waiting_for_feedback_day91_4_no))
async def process_feedback_day91_4_no(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Какие были ожидания от компании"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)
    lang = await get_language_from_server(user_id)
    await message.answer(translate(lang, 'day91_5'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day91_5_yes")],
                             [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day91_5_no")]
                         ]))
    await state.clear()


@button91_router.callback_query(F.data == "day91_5_yes")
async def handle_day91_5_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day91_5_yes'))
    await asyncio.sleep(1)
    await callback.message.answer(translate(lang, 'day91_6'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day91_6_answer")]
                                  ]))
    await callback.answer()


@button91_router.callback_query(F.data == "day91_5_no")
async def handle_day91_5_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day91_5_no'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day91_5_no_answer")]
                                  ]))
    await callback.answer()


@button91_router.callback_query(F.data == "day91_5_no_answer")
async def handle_day91_5_no_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_91.waiting_for_feedback_day91_5_no)
    await callback.answer()


@button91_router.message(StateFilter(NewMessageStates_91.waiting_for_feedback_day91_5_no))
async def process_feedback_day91_5_no(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Почему не смог достигнуть поставленных целей"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)
    lang = await get_language_from_server(user_id)
    await message.answer(translate(lang, 'day91_6'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day91_6_answer")]
                         ]))
    await state.clear()


@button91_router.callback_query(F.data == "day91_6_answer")
async def handle_day91_6_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_91.waiting_for_feedback_day91_6)
    await callback.answer()


@button91_router.message(StateFilter(NewMessageStates_91.waiting_for_feedback_day91_6))
async def process_feedback_day91_6(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Общий за все 91 дней"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)
    lang = await get_language_from_server(user_id)
    await message.answer(translate(lang, 'day91_thanks'))
    await state.clear()


@button91_router.callback_query(F.data.in_({"evening_1", "evening_2", "evening_3", "evening_4", "evening_5"}))
async def process_evening_buttons(callback: CallbackQuery, state: FSMContext):
    rating_value = callback.data.split('_')[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    message_type = 'Оценка бота 91 день'
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, rating_value, current_time)
    await asyncio.sleep(1)
    lang = await get_language_from_server(user_id)
    feedback_message = translate(lang, 'day91_evening_message_2')
    await callback.message.edit_text(
        feedback_message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="reply_suggestion_91")]
            ]
        )
    )


@button91_router.callback_query(F.data == "reply_suggestion_91")
async def process_reply_suggestion_91(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_91.waiting_for_feedback_day91_ev_91)


@button91_router.message(F.text, StateFilter(NewMessageStates_91.waiting_for_feedback_day91_ev_91))
async def process_suggestion_response_91(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Предложение по доработкe бота 91 день"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day91_last_message')
    await message.answer(thanks_message)
    await state.clear()


def start_scheduling_91():
    scheduler.start()