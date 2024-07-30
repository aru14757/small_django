import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

useful_info_router = Router(name="useful_info_router")

@useful_info_router.callback_query(F.data == "useful_info")
async def useful_info(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(state)
    name = callback.from_user.full_name
    text = (
        f"{translate(lang, 'menu_useful_info').format(name=name)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard = [
                [InlineKeyboardButton(text="1", callback_data="option_1"),
                 InlineKeyboardButton(text="2", callback_data="option_2"),
                 InlineKeyboardButton(text="3", callback_data="option_3"),
                 InlineKeyboardButton(text="4", callback_data="option_4")],
                [InlineKeyboardButton(text="5", callback_data="option_5"),
                 InlineKeyboardButton(text="6", callback_data="option_6"),
                 InlineKeyboardButton(text="7", callback_data="option_7"),
                 InlineKeyboardButton(text="8", callback_data="option_8")],
                [InlineKeyboardButton(text="0", callback_data="menu")]
    ]
        )

    )

