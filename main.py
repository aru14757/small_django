import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from bot.routers.сheck import check_user_exists
from bot.lang import get_language, translate
from bot.routers.language import language_router
from bot.routers.useful_info import useful_info_router
from bot.routers.useful.option_3 import option_3_router
from bot.routers.useful.option_4 import option_4_router, option_progress, option_elma, option_swapp, option_bimoid
from bot.routers.useful.options import option_1_router, option_2_router, option_5_router, option_6_router, option_7_router, \
    option_8_router
from bot.routers.useful.option_3 import choice_1_router, choice_2_router, choice_3_router, choice_4_router, choice_7_router, \
    choice_8_router, choice_10_router, choice_11_router, choice_12_router
from bot.routers.useful.choice_5 import choice_5_1, choice_5_2, choice_5_3, choice_5_router
from bot.routers.useful.choice_6 import choice_6_1, choice_6_2, choice_6_3, choice_6_4, choice_6_router
from bot.routers.useful.choice_9 import choice_9_1, choice_9_2, choice_9_router

from bot.routers.useful.option_3 import send_option_3_message_answer
from bot.days.day1 import start_scheduler, schedule_user_messages, button_1_router,ch_1_router,ch_2_router,ch_3_router
from bot.days.new_messages import new_scheduler, schedule_messages_for_employees, schedule_messages_for_managers
from bot.days.day5 import button_5_router,start_scheduler_5,schedule_user_messages_5
from bot.days.day31 import button31_router, set_message_schedule_31,start_scheduling_31
from bot.days.day14 import feedback_router,start_scheduling_14,schedule_day14_messages
from bot.days.day27 import button_router,set_message_schedule,start_scheduling
from bot.days.day45 import feedback_45_router,start_scheduling_45,schedule_day45_messages
from bot.days.day61 import start_scheduling_61,set_message_schedule_61,button61_router
from bot.days.day7 import start_scheduling_7,set_message_schedule_7,button7_router
from bot.days.day91 import set_message_schedule_91,button91_router,start_scheduling_91
load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    logging.info("Команда /start вызвана")

    user_id = message.from_user.id
    username = message.from_user.username

    await message.answer(
        f"Сәлеметсіз бе {message.from_user.full_name}?! Тілді таңдаңыз.\nЗдравствуйте {message.from_user.full_name}, выберите язык.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Қазақ тілі 🇰🇿", callback_data="kk"),
                    InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru")
                ]
            ]
        )
    )



@dp.message(Command("menu"))
async def command_menu(message: Message, state: FSMContext):
    logging.info("Команда /menu вызвана")
    lang = await get_language(state)
    if not check_user_exists(message.from_user.id):
        text = translate(lang, "employee_not_found")
        await message.answer(text)  # Changed message_id.answer_text to message.answer
    else:
        await message.answer(translate(lang, "menu"), reply_markup=generate_menu_buttons(lang))




@dp.message(Command("help"))
async def command_help(message: Message, state: FSMContext):
    logging.info("Команда /help вызвана")
    lang = await get_language(state)
    if not check_user_exists(message.from_user.id):
        text = translate(lang, "employee_not_found")
        await message.answer(text)  # Changed message_id.answer_text to message.answer
    else:
        await send_option_3_message_answer(message.from_user.full_name, message, state)



@dp.callback_query(lambda callback: callback.data == "menu")
async def menu_handler(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(state)
    await callback.message.edit_text(translate(lang, "menu"), reply_markup=generate_menu_buttons(lang))


def generate_menu_buttons(lang: str = "kk"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{translate(lang, 'change_language')} 🌐",
                    callback_data="change_language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{translate(lang, 'useful_info')} 📚",
                    callback_data="useful_info"
                )
            ]
        ]
    )


async def main():
    dp.include_routers(
        language_router,
        useful_info_router,
        option_1_router,
        option_2_router,
        option_3_router,
        option_4_router,
        option_5_router,
        option_6_router,
        option_7_router,
        option_8_router,
        option_progress,
        option_elma,
        option_swapp,
        option_bimoid,
        choice_1_router,
        choice_2_router,
        choice_3_router,
        choice_4_router,
        choice_5_router,
        choice_5_1,
        choice_5_2,
        choice_5_3,
        choice_6_router,
        choice_6_1,
        choice_6_2,
        choice_6_3,
        choice_6_4,
        choice_7_router,
        choice_8_router,
        choice_9_router,
        choice_10_router,
        choice_11_router,
        choice_12_router,
        choice_9_1,
        choice_9_2,
        button_1_router,
        ch_1_router,
        ch_2_router,
        ch_3_router,
        button_5_router,
        feedback_router,
        button_router,
        feedback_45_router,
        button31_router,
        button61_router,
        button7_router,
        button91_router
    )

    start_scheduler()
    schedule_user_messages(bot)
    new_scheduler()
    schedule_messages_for_employees(bot)
    schedule_messages_for_managers(bot)
    start_scheduler_5()
    await schedule_user_messages_5(bot)
    start_scheduling_14()
    schedule_day14_messages(bot)
    set_message_schedule(bot)
    start_scheduling()
    start_scheduling_45()
    schedule_day45_messages(bot)
    set_message_schedule_31(bot)
    start_scheduling_31()
    start_scheduling_61()
    set_message_schedule_61(bot)
    start_scheduling_7()
    set_message_schedule_7(bot)
    set_message_schedule_91(bot)
    start_scheduling_91()

    await set_main_menu(bot)
    await dp.start_polling(bot, skip_updates=True)


    await set_main_menu(bot)
    await dp.start_polling(bot)


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command="start",
            description="Бастау/Старт"
        ),
        BotCommand(
            command="menu",
            description="Мәзір/Меню"
        ),
        BotCommand(
            command="help",
            description="Пайдалы ақпарат/Полезная информация"
        ),
    ]
    await bot.set_my_commands(main_menu_commands)
    logging.info("Основные команды бота установлены")


if __name__ == '__main__':
    asyncio.run(main())