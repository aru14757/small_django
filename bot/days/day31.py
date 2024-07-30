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

class NewMessageStates_31(StatesGroup):
    waiting_for_response_31 = State()
    waiting_for_feedback_31 = State()
    waiting_for_answer_unclear_31 = State()

button31_router = Router(name="button31_router")
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
        if message_type == 'day_31':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day_31_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day_31_no")]
            ])
        elif message_type == 'day_31_1':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day_31_1_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day_31_1_no")]
            ])
        elif message_type == 'day_31_1_1':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day_31_1_1_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day_31_1_1_no")]
            ])
        elif message_type == 'day_31_why_no':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day_31_why_no_answer")]
            ])
        elif message_type == 'day_31_2':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "back"), callback_data="day_31_back")]
            ])
        elif message_type == 'day31_trening':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day31_trening_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day31_trening_no")]
            ])
        elif message_type == 'day31_trening_yes':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day31_trening_yes_answer")]
            ])
        elif message_type == 'day31_trening_no':
            keyboard = None
        elif message_type == 'day31_if_something_unclear':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day31_unclear_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day31_unclear_no")]
            ])
        elif message_type == 'day31_unclear_yes':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day31_unclear_yes_answer")]
            ])
        elif message_type == 'day31_unclear_no':
            keyboard = None

        await schedule_message(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")


def set_message_schedule_31(bot: Bot):
    users = read_employee_data()
    for user in users:
        chat_id = user['telegram_id']
        username = user['name']
        first_day_str = user.get('first_day')  # Get first_day as a string

        if first_day_str is None:
            logging.warning(f"No first_day value for user {username}")
            continue

        try:
            first_day = datetime.strptime(first_day_str, '%Y-%m-%d').date()
        except ValueError as e:
            logging.error(f"Error converting first_day string to date for user {username}: {e}")
            continue

        day31_date = first_day + timedelta(days=30)

        times = {
            'day_31': time(7, 30),
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(day31_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@button31_router.callback_query(F.data == "day_31_no")
async def handle_day_31_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31_2'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "back"), callback_data="day_31_back")]
                                  ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_back")
async def handle_day_31_back(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31'))
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day_31_yes")],
        [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day_31_no")]
    ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_no")
async def handle_day_31_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31_2'))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_yes")
async def handle_day_31_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31_1'))
    await asyncio.sleep(1)
    await callback.message.answer(translate(lang, 'day_31_1_1'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day_31_1_1_yes")],
                                      [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day_31_1_1_no")]
                                  ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_1_1_yes")
async def handle_day_31_1_1_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'no_doubt'))
    await asyncio.sleep(1.5)
    await callback.message.edit_text(translate(lang, 'day31_trening'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day31_trening_yes")],
                                      [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day31_trening_no")]
                                  ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_1_1_no")
async def handle_day_31_1_1_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31_why_no'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day_31_why_no_answer")]
                                  ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day_31_why_no_answer")
async def handle_day_31_why_no_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_31.waiting_for_response_31)
    await callback.answer()


@button31_router.callback_query(F.data == "day31_trening_yes_answer")
async def handle_day31_trening_yes_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_31.waiting_for_feedback_31)
    await callback.answer()


@button31_router.message(StateFilter(NewMessageStates_31.waiting_for_response_31))
async def process_suggestion_response_31(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Почему не оправдались ожидания?"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    await message.answer(translate(lang, 'day31_trening'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day31_trening_yes")],
                             [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day31_trening_no")]
                         ]))
    await state.clear()


@button31_router.callback_query(F.data == "day31_trening_yes")
async def handle_day31_trening_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day31_trening_yes'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day31_trening_yes_answer")]
                                  ]))
    await callback.answer()



@button31_router.callback_query(F.data == "day31_trening_no")
async def handle_day31_trening_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day31_trening_no'))
    await callback.message.edit_text(translate(lang, 'day31_if_something_unclear'),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text=translate(lang, "Yes"),
                                                               callback_data="day31_unclear_yes")],
                                         [InlineKeyboardButton(text=translate(lang, "No"),
                                                               callback_data="day31_unclear_no")]
                                     ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day31_trening_yes_answer")
async def handle_day31_trening_yes_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_31.waiting_for_feedback_31)
    await callback.answer()


@button31_router.message(StateFilter(NewMessageStates_31.waiting_for_feedback_31))
async def process_feedback_31(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "О тренинге"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    await message.answer(translate(lang, 'day31_if_something_unclear'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day31_unclear_yes")],
                             [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day31_unclear_no")]
                         ]))
    await state.clear()


@button31_router.callback_query(F.data == "day31_unclear_yes")
async def handle_day31_unclear_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day31_unclear_yes'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day31_unclear_yes_answer")]
                                  ]))
    await callback.answer()


@button31_router.callback_query(F.data == "day31_unclear_no")
async def handle_day31_unclear_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day31_unclear_no'))
    await callback.answer()


@button31_router.callback_query(F.data == "day31_unclear_yes_answer")
async def handle_day31_unclear_yes_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_31.waiting_for_answer_unclear_31)
    await callback.answer()


@button31_router.message(StateFilter(NewMessageStates_31.waiting_for_answer_unclear_31))
async def process_answer_unclear_31(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Что то было не понятно?"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)
    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day31_unclear_no')
    await message.answer(thanks_message)
    await state.clear()


def start_scheduling_31():
    scheduler.start()