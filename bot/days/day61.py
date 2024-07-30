from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, time, timedelta
import logging
from bot.routers.utils import read_employee_data, send_feedback_to_server, get_language_from_server
from bot.lang.kk import kk
from bot.lang.ru import ru
from bot.lang import translate
from aiogram.filters import StateFilter

logging.basicConfig(level=logging.INFO)

class NewMessageStates_61(StatesGroup):
    waiting_for_button_61 = State()
    waiting_for_feedback_61 = State()

button61_router = Router(name="button61_router")
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
        if message_type == 'day61_1':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day61_1_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day61_1_no")]
            ])
        elif message_type == 'day61_1_yes':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day61_1_yes_1")],
                [InlineKeyboardButton(text="2", callback_data="day61_1_yes_2")],
                [InlineKeyboardButton(text="3", callback_data="day61_1_yes_3")],
                [InlineKeyboardButton(text="4", callback_data="day61_1_yes_4")],
                [InlineKeyboardButton(text="5", callback_data="day61_1_yes_5")]
            ])
        elif message_type == 'day61_about_employer':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day61_about_employer_1")],
                [InlineKeyboardButton(text="2", callback_data="day61_about_employer_2")],
                [InlineKeyboardButton(text="3", callback_data="day61_about_employer_3")],
                [InlineKeyboardButton(text="4", callback_data="day61_about_employer_4")],
                [InlineKeyboardButton(text="5", callback_data="day61_about_employer_5")]
            ])
        elif message_type == 'day61_about_team':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day61_about_team_1")],
                [InlineKeyboardButton(text="2", callback_data="day61_about_team_2")],
                [InlineKeyboardButton(text="3", callback_data="day61_about_team_3")],
                [InlineKeyboardButton(text="4", callback_data="day61_about_team_4")],
                [InlineKeyboardButton(text="5", callback_data="day61_about_team_5")]
            ])
        elif message_type == 'day61_about_division':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day61_about_division_1")],
                [InlineKeyboardButton(text="2", callback_data="day61_about_division_2")],
                [InlineKeyboardButton(text="3", callback_data="day61_about_division_3")],
                [InlineKeyboardButton(text="4", callback_data="day61_about_division_4")],
                [InlineKeyboardButton(text="5", callback_data="day61_about_division_5")]
            ])
        elif message_type == 'day61_suggesion':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="reply_61")]
            ])
        elif message_type == 'day61_1_no':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "back"), callback_data="day61_1_back")]
            ])

        await schedule_message(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")


def set_message_schedule_61(bot: Bot):
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

        day61_date = first_day + timedelta(days=60)

        times = {
            'day61_1': time(8, 0),
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(day61_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@button61_router.callback_query(F.data == "day61_1_no")
async def handle_day61_1_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_1_no'),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text=translate(lang, "back"), callback_data="day61_1_back")]
                                     ]))
    await callback.answer()


@button61_router.callback_query(F.data == "day61_1_back")
async def handle_day61_1_back(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_1'))
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day61_1_yes")],
        [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day61_1_no")]
    ]))
    await callback.answer()


@button61_router.callback_query(F.data == "day61_1_yes")
async def handle_day61_1_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_1_yes'),  #
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_1_yes_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_1_yes_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_1_yes_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_1_yes_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_1_yes_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data.startswith("day61_1_yes_"))
async def handle_day61_1_yes_feedback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    button_value = callback.data.split("_")[-1]
    current_time = datetime.now().isoformat()

    # Save feedback to the server
    send_feedback_to_server(username, user_id, "Day61 Feedback", button_value, current_time)

    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_employer'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_employer_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_employer_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_employer_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_employer_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_employer_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data == "day61_about_employer")
async def handle_day61_about_employer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_employer'),  # Ensure this message is translated
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_employer_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_employer_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_employer_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_employer_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_employer_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data.startswith("day61_about_employer_"))
async def handle_day61_about_employer_feedback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    button_value = callback.data.split("_")[-1]
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, "Day61 Feedback employer", button_value, current_time)

    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_team'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_team_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_team_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_team_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_team_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_team_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data == "day61_about_team_")
async def handle_day61_about_team(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_division'),  # Ensure this message is translated
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_division_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_division_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_division_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_division_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_division_5")]
                                  ]))
    await callback.answer()

@button61_router.callback_query(F.data.startswith("day61_about_team"))
async def handle_day61_about_team_feedback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    button_value = callback.data.split("_")[-1]
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, "Day61 Feedback team", button_value, current_time)

    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_division'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_division_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_division_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_division_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_division_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_division_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data == "day61_about_division")
async def handle_day61_about_division(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day61_about_division'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text="1", callback_data="day61_about_division_1")],
                                      [InlineKeyboardButton(text="2", callback_data="day61_about_division_2")],
                                      [InlineKeyboardButton(text="3", callback_data="day61_about_division_3")],
                                      [InlineKeyboardButton(text="4", callback_data="day61_about_division_4")],
                                      [InlineKeyboardButton(text="5", callback_data="day61_about_division_5")]
                                  ]))
    await callback.answer()


@button61_router.callback_query(F.data.startswith("day61_about_division_"))
async def handle_day61_about_division_feedback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    button_value = callback.data.split("_")[-1]
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, "Day61 Feedback division", button_value, current_time)

    lang = await get_language_from_server(user_id)
    feedback_message = translate(lang, 'day61_suggesion')
    await callback.message.edit_text(
        feedback_message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="reply_61")]
            ]
        )
    )


@button61_router.callback_query(F.data == "reply_61")
async def process_reply_61(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_61.waiting_for_feedback_61)  # Устанавливаем состояние ожидания сообщения


@button61_router.message(F.text, StateFilter(NewMessageStates_61.waiting_for_feedback_61))
async def process_suggestion_response_61(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Исходя из предыдущих вопросов, что компания могла бы улучшить?"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()
    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)
    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day61_thanks')
    await message.answer(thanks_message)
    await state.clear()


def start_scheduling_61():
    scheduler.start()