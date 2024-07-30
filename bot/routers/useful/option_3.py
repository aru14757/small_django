from aiogram.filters import Command

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

option_3_router = Router(name="option_3_router")

@option_3_router.callback_query(F.data == "option_3")
async def option_3(callback: CallbackQuery, state: FSMContext):
    await send_option_3_message_edit(callback.from_user.full_name, callback.message, state)

async def send_option_3_message_answer(name: str, message: Message, state: FSMContext):
    lang = await get_language(state)
    text = f"{translate(lang, 'option_3').format(name=name)}"
    await message.answer(
        text,
        reply_markup=generate_option_3_markup(lang)
    )

async def send_option_3_message_edit(name: str, message: Message, state: FSMContext):
    lang = await get_language(state)
    text = f"{translate(lang, 'option_3').format(name=name)}"
    await message.edit_text(
        text,
        reply_markup=generate_option_3_markup(lang)
    )

def generate_option_3_markup(lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1", callback_data="choice_1"),
             InlineKeyboardButton(text="2", callback_data="choice_2"),
             InlineKeyboardButton(text="3", callback_data="choice_3"),
             InlineKeyboardButton(text="4", callback_data="choice_4")],
            [InlineKeyboardButton(text="5", callback_data="choice_5"),
             InlineKeyboardButton(text="6", callback_data="choice_6"),
             InlineKeyboardButton(text="7", callback_data="choice_7"),
             InlineKeyboardButton(text="8", callback_data="choice_8")],
            [InlineKeyboardButton(text="9", callback_data="choice_9"),
             InlineKeyboardButton(text="10", callback_data="choice_10"),
             InlineKeyboardButton(text="11", callback_data="choice_11"),
             InlineKeyboardButton(text="12", callback_data="choice_12")],
            [InlineKeyboardButton(text=translate(lang, "back"), callback_data="useful_info")]
        ]
    )

@option_3_router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    await send_option_3_message_answer(message.from_user.full_name, message, state)

def create_router(choice_number: int, translation_key: str):
    router = Router(name=f"choice_{choice_number}_router")

    @router.callback_query(F.data == f"choice_{choice_number}")
    async def handle_callback(callback: CallbackQuery, state: FSMContext):
        lang = await get_language(state)
        name = callback.from_user.full_name
        text = (
            f"{translate(lang, translation_key).format(name=name)}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="option_3")]
                ]
            )
        )

    return router


choice_1_router = create_router(1, 'choice_1')
choice_2_router = create_router(2, 'choice_2')
choice_3_router = create_router(3, 'choice_3')
choice_4_router = create_router(4, 'choice_4')
choice_7_router = create_router(7, 'choice_7')
choice_8_router = create_router(8, 'choice_8')
choice_10_router = create_router(10, 'choice_10')
choice_11_router = create_router(11, 'choice_11')
choice_12_router = create_router(12, 'choice_12')
