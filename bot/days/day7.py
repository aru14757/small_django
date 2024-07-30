from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
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

class Day7FeedbackStates(StatesGroup):
    awaiting_suggestion = State()
    awaiting_suggestion_4 = State()
class NewSuggestionStates(StatesGroup):
    waiting_for_feedback = State()
class NewMessageStates_7(StatesGroup):
    waiting_for_feedback_day7_yes2 = State()
    waiting_for_feedback_day7_yes3 = State()
    waiting_for_feedback_day7_nastavnik = State()
    waiting_for_answer_unclear_day7_nastavnik = State()


button7_router = Router(name="button7_router")
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
        if message_type == 'day_7':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day_7_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day_7_no")]
            ])
        elif message_type == 'day_31_2':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "back"), callback_data="day_7_back")]
            ])
        elif message_type == 'day7_yes2':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day7_yes2_answer")]
            ])
        elif message_type == 'day7_yes3':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day7_yes3_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day7_yes3_no")]
            ])
        elif message_type == 'day7_yes3_yes':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day7_yes3_yes_answer")]
            ])
        elif message_type == 'day7_nastavnik':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "Yes"), callback_data="day7_nastavnik_yes")],
                [InlineKeyboardButton(text=translate(user_lang, "No"), callback_data="day7_nastavnik_no")]
            ])
        elif message_type == 'day7_nastavnik_no':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day7_nastavnik_no_answer")]
            ])
        elif message_type == 'day7_last':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="day7_last_answer")]
            ])
        elif message_type == 'mood_ask1':
            keyboard = None
        elif message_type == 'mood_ask2':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="day14_button_1")],
                [InlineKeyboardButton(text="2", callback_data="day14_button_2")],
                [InlineKeyboardButton(text="3", callback_data="day14_button_3")],
                [InlineKeyboardButton(text="4", callback_data="day14_button_4")]
            ])
        elif message_type == 'giving_rate':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="rating_1")],
                [InlineKeyboardButton(text="2", callback_data="rating_2")],
                [InlineKeyboardButton(text="3", callback_data="rating_3")],
                [InlineKeyboardButton(text="4", callback_data="rating_4")],
                [InlineKeyboardButton(text="5", callback_data="rating_5")]
            ])
        elif message_type == 'day7_3_buttons':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=translate(user_lang, "answer"), callback_data="reply_suggestion")]
            ])

        await schedule_message(bot, chat_id, message_text, keyboard)
    else:
        logging.info(f"Message not sent to {username} as they are not a worker.")


def set_message_schedule_7(bot: Bot):
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

        day7_date = first_day + timedelta(days=6)

        times = {
            'day_7': time(10, 0),
            'giving_rate': time(16, 0),
            'mood_ask1': time(17, 0),
            'mood_ask2': time(17, 0, 5),
        }

        for message_type, send_time in times.items():
            scheduled_time = datetime.combine(day7_date, send_time)
            if scheduled_time > datetime.now():
                scheduler.add_job(prepare_message, DateTrigger(run_date=scheduled_time),
                                  args=[bot, chat_id, username, message_type])


@button7_router.callback_query(F.data == "day_7_no")
async def handle_day_7_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_31_2'),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text=translate(lang, "back"),
                                                               callback_data="day_7_back")]
                                     ]))
    await callback.answer()


@button7_router.callback_query(F.data == "day_7_back")
async def handle_day_7_back(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day_7'),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day_7_yes")],
                                         [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day_7_no")]
                                     ]))
    await callback.answer()


@button7_router.callback_query(F.data == "day_7_yes")
async def handle_day_7_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)

    await callback.message.edit_text(translate(lang, 'day7_yes1'))

    await callback.message.answer(translate(lang, 'day7_yes2'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"),
                                                            callback_data="day7_yes2_answer")]
                                  ]))

    await callback.answer()


@button7_router.callback_query(F.data == "day7_yes2_answer")
async def handle_day7_yes2_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)

    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_7.waiting_for_feedback_day7_yes2)
    await callback.answer()


@button7_router.message(StateFilter(NewMessageStates_7.waiting_for_feedback_day7_yes2))
async def process_feedback_day7_yes2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "О 7 дне"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)

    # Send day7_yes3 immediately
    await message.answer(translate(lang, 'day7_yes3'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "Yes"), callback_data="day7_yes3_yes")],
                             [InlineKeyboardButton(text=translate(lang, "No"), callback_data="day7_yes3_no")]
                         ]))
    await state.clear()


@button7_router.callback_query(F.data == "day7_yes3_no")
async def handle_day7_yes3_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day7_yes3_no'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "answer"),
                                                            callback_data="day7_yes3_no_answer")]
                                  ]))
    await state.set_state(NewMessageStates_7.waiting_for_feedback_day7_yes3)
    await callback.answer()


@button7_router.callback_query(F.data == "day7_yes3_yes")
async def handle_day7_yes3_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'no_doubt'))
    await asyncio.sleep(1)  # Wait for 1 second
    # Send day7_nastavnik with Yes and No buttons
    await callback.message.answer(translate(lang, 'day7_nastavnik'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, "Yes"),
                                                            callback_data="day7_nastavnik_yes")],
                                      [InlineKeyboardButton(text=translate(lang, "No"),
                                                            callback_data="day7_nastavnik_no")]
                                  ]))
    await state.clear()
    await callback.answer()



@button7_router.callback_query(F.data == "day7_yes3_no_answer")
async def handle_day7_yes3_no_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)

    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_7.waiting_for_feedback_day7_yes3)
    await callback.answer()


@button7_router.message(StateFilter(NewMessageStates_7.waiting_for_feedback_day7_yes3))
async def process_feedback_day7_yes3(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "О том чего не хватает"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    await asyncio.sleep(1)
    # Send day7_nastavnik with Yes and No buttons
    await message.answer(translate(lang, 'day7_nastavnik'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "Yes"),
                                                   callback_data="day7_nastavnik_yes")],
                             [InlineKeyboardButton(text=translate(lang, "No"),
                                                   callback_data="day7_nastavnik_no")]
                         ]))

    await state.clear()


@button7_router.callback_query(F.data == "day7_nastavnik_yes")
async def handle_day7_nastavnik_yes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day7_nastavnik_yes'))
    await asyncio.sleep(1)  # Wait for 1 second
    # Send day7_last after day7_nastavnik_yes
    await callback.message.answer(translate(lang, 'day7_last'),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text=translate(lang, "answer"),
                                                               callback_data="day7_last_answer")]
                                     ]))
    await state.clear()
    await callback.answer()


@button7_router.callback_query(F.data == "day7_nastavnik_no")
async def handle_day7_nastavnik_no(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.edit_text(translate(lang, 'day7_nastavnik_no'),
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [InlineKeyboardButton(text=translate(lang, 'answer'),
                                                            callback_data="day7_nastavnik_no_answer")]
                                  ]))
    await callback.answer()


@button7_router.callback_query(F.data == "day7_nastavnik_no_answer")
async def handle_day7_nastavnik_no_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_7.waiting_for_feedback_day7_nastavnik)
    await callback.answer()


@button7_router.message(StateFilter(NewMessageStates_7.waiting_for_feedback_day7_nastavnik))
async def process_feedback_day7_nastavnik(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "О наставнике"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)

    await message.answer(translate(lang, 'day7_thanks'))

    await asyncio.sleep(1)

    await message.answer(translate(lang, 'day7_last'),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day7_last_answer")]
                         ]))

    await state.clear()


@button7_router.callback_query(F.data == "day7_last_answer")
async def handle_day7_last_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(NewMessageStates_7.waiting_for_answer_unclear_day7_nastavnik)
    await callback.answer()


@button7_router.message(StateFilter(NewMessageStates_7.waiting_for_answer_unclear_day7_nastavnik))
async def process_feedback_day7_last_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    message_type = "Свои вопросы"
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, suggestion_text, current_time)

    lang = await get_language_from_server(user_id)

    await message.answer(translate(lang, 'day7_good_day'))

    await state.clear()


@button7_router.callback_query(F.data.in_({"day14_button_1", "day14_button_2", "day14_button_3", "day14_button_4"}))
async def handle_day14_buttons(callback: CallbackQuery, state: FSMContext):
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
        # Use reply_markup to ensure the button is included in the message
        await callback.message.edit_text(response_message, reply_markup=keyboard)
        await state.set_state(Day7FeedbackStates.awaiting_suggestion)
    elif message_type == "day14_button_4":
        response_message = translate(lang, 'day14_button4')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="day14_suggestion_reply_4")]
        ])
        await callback.message.edit_text(response_message, reply_markup=keyboard)
        await state.set_state(Day7FeedbackStates.awaiting_suggestion_4)

    feedback = callback.data.split('_')[-1]
    send_feedback_to_server(username, user_id, "1.Мне комфортно😊\n2.Я чувствую себя увереннее😏\n3.У меня не все получается🦾\n4.Слишком много всего, я устаю😣", feedback, datetime.now().isoformat())

@button7_router.callback_query(F.data == "day14_suggestion_reply")
async def handle_suggestion_reply(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(Day7FeedbackStates.awaiting_suggestion)

@button7_router.callback_query(F.data == "day14_suggestion_reply_4")
async def handle_suggestion_reply_4(callback: CallbackQuery, state: FSMContext):
    lang = await get_language_from_server(callback.from_user.id)
    await callback.message.answer(translate(lang, 'please_write_suggestion'))
    await state.set_state(Day7FeedbackStates.awaiting_suggestion_4)

@button7_router.message(F.text, StateFilter(Day7FeedbackStates.awaiting_suggestion))
async def handle_suggestion_response(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, "Problem of 14th day", suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day14_thanks')
    await message.answer(thanks_message)

    await state.clear()

@button7_router.message(F.text, StateFilter(Day7FeedbackStates.awaiting_suggestion_4))
async def handle_suggestion_response_4(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    suggestion_text = message.text
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, "Problem of 14th day", suggestion_text, current_time)

    lang = await get_language_from_server(user_id)
    thanks_message = translate(lang, 'day14_thanks')
    await message.answer(thanks_message)

    await state.clear()


@button7_router.callback_query(F.data.in_({"rating_1", "rating_2", "rating_3", "rating_4", "rating_5"}))
async def process_rating_buttons(callback: CallbackQuery, state: FSMContext):
    rating_value = callback.data.split('_')[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    message_type = 'Оценка бота 7'
    current_time = datetime.now().isoformat()

    send_feedback_to_server(username, user_id, message_type, rating_value, current_time)

    await asyncio.sleep(1)
    lang = await get_language_from_server(user_id)
    feedback_message = translate(lang, 'day27_3_buttons')
    await callback.message.answer(
        feedback_message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "answer"), callback_data="reply_suggestion")]
            ]
        )
    )


@button7_router.callback_query(F.data == "reply_suggestion")
async def process_reply_suggestion(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_language_from_server(user_id)
    await callback.message.answer(translate(lang, 'day27_3_buttons'))
    await state.set_state(NewSuggestionStates.waiting_for_feedback)


@button7_router.message(F.text, StateFilter(NewSuggestionStates.waiting_for_feedback))
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

def start_scheduling_7():
    scheduler.start()
