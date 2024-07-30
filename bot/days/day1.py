import logging
import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from bot.routers.utils import read_employee_data, get_language_from_server, send_feedback_to_server
from bot.lang import kk, ru, translate
from bot.states import SuggestionStates
from aiogram.filters import StateFilter
from bot.routers.useful_info import useful_info

logging.basicConfig(level=logging.INFO)

button_1_router = Router(name="button_1_router")
scheduler = AsyncIOScheduler()


async def send_scheduled_message(bot: Bot, chat_id, message_text, keyboard=None):
    logging.info(f"Sending message to {chat_id}: {message_text}")
    await bot.send_message(chat_id, message_text, reply_markup=keyboard)


async def get_user_message_text(user_lang, message_type, username):
    messages = {
        'kk': kk,
        'ru': ru
    }
    message_text_template = messages.get(user_lang, ru).get(message_type, "")
    return message_text_template.format(name=username)


async def send_message_with_updated_language(bot: Bot, chat_id, username, message_type):
    # Fetch user's language from server
    user_lang = await get_language_from_server(chat_id)
    message_text = await get_user_message_text(user_lang, message_type, username)

    keyboards = {
        'smile_ask': InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😊", callback_data="good")],
            [InlineKeyboardButton(text="😐", callback_data="normal")],
            [InlineKeyboardButton(text="😞", callback_data="bad")]
        ]),
        'hello_employee': InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1", callback_data="1")]
        ]),
        'suggestion': InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="reply_suggestion")]
        ])
    }
    keyboard = keyboards.get(message_type, None)
    await send_scheduled_message(bot, chat_id, message_text, keyboard)


def schedule_user_messages(bot: Bot):
    users = read_employee_data()
    for user in users:
        chat_id = user['telegram_id']
        username = user['name']
        first_day_str = user.get('first_day')
        role = user.get('role')

        if role not in ["security", "shop", "office","support"]:
            logging.info(f"Skipping user {username} with role {role}")
            continue

        if first_day_str is None:
            logging.warning(f"No first_day value for user {username}")
            continue

        try:
            first_day = datetime.strptime(first_day_str, '%Y-%m-%d').date()
        except ValueError as e:
            logging.error(f"Error converting first_day string to date for user {username}: {e}")
            continue

        times = {
            'hello_employee': time(8, 00),
            'smile_ask': time(20, 00),
            'suggestion': time(20, 10)
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(first_day, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(send_message_with_updated_language, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@button_1_router.callback_query(F.data.in_({"good", "normal", "bad"}))
async def handle_smile_buttons(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    feedback = callback.data
    thanks_text = translate(lang, 'thanks_for_response')
    await callback.message.edit_reply_markup(InlineKeyboardMarkup(inline_keyboard=[]))
    await callback.message.answer(thanks_text)

    user_id = callback.from_user.id
    username = callback.from_user.username
    message_type = 'smile_ask'
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, feedback, current_time)

    await asyncio.sleep(2)
    next_thanks_text = translate(lang, 'next_thanks_for_response')
    await callback.message.answer(next_thanks_text)


@button_1_router.callback_query(F.data == "reply_suggestion")
async def handle_reply_suggestion(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(SuggestionStates.waiting_for_answer)


@button_1_router.message(F.text, StateFilter(SuggestionStates.waiting_for_answer))
async def handle_suggestion_response(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    suggestion = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, 'suggestion', suggestion, current_time)

    lang = await get_language_from_server(user_id)  # Fetch language from server
    thanks_text = translate(lang, 'thanks_for_suggestion')
    await message.answer(thanks_text)

    await state.clear()


@button_1_router.callback_query(F.data == "1")
async def handle_button_1(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    text = translate(lang, 'next_message')
    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="ch_1")],
                [InlineKeyboardButton(text="2", callback_data="ch_2")],
                [InlineKeyboardButton(text="3", callback_data="ch_3")]
            ]
        )
    )


def create_router(ch_number: int, translation_key: str):
    router = Router(name=f"ch_{ch_number}_router")

    @router.callback_query(F.data == f"ch_{ch_number}")
    async def handle_callback(callback: CallbackQuery, state: FSMContext):
        lang = await get_language_from_server(callback.from_user.id)
        text = translate(lang, translation_key)
        if ch_number == 3:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="ch_3_1")],
                [InlineKeyboardButton(text="2", callback_data="ch_3_2")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="back_to_next_message")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="back_to_next_message")]
            ])
        await callback.message.edit_text(
            text,
            reply_markup=keyboard
        )

    return router


@button_1_router.callback_query(F.data == "ch_3_1")
async def handle_ch_3_1(callback: CallbackQuery, state: FSMContext):
    await useful_info(callback, state)


@button_1_router.callback_query(F.data == "ch_3_2")
async def handle_ch_3_2(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)  # Fetch language from server
    text = translate(lang, 'day_1_3_2')
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="back_to_day_1_3")]
            ]
        )
    )


@button_1_router.callback_query(F.data == "back_to_day_1_3")
async def handle_back_to_day_1_3(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    text = translate(lang, 'day_1_3')
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="ch_3_1")],
                [InlineKeyboardButton(text="2", callback_data="ch_3_2")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="back_to_next_message")]
            ]
        )
    )


@button_1_router.callback_query(F.data == "back_to_next_message")
async def handle_back_to_next_message(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    text = translate(lang, 'next_message')
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="ch_1")],
                [InlineKeyboardButton(text="2", callback_data="ch_2")],
                [InlineKeyboardButton(text="3", callback_data="ch_3")]
            ]
        )
    )


ch_1_router = create_router(1, 'day_1_1')
ch_2_router = create_router(2, 'day_1_2')
ch_3_router = create_router(3, 'day_1_3')


def start_scheduler():
    scheduler.start()