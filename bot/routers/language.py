import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.lang import translate, get_language, set_language
from bot.routers.сheck import check_user_exists
from bot.routers.utils import update_user_language

logging.basicConfig(level=logging.INFO)

language_router = Router(name="language_router")

@language_router.callback_query(F.data == "change_language")
async def change_language(callback: CallbackQuery, state: FSMContext):
    print("lang change router")
    lang = await get_language(state)
    back_text = f"{translate(lang, 'back')} -> {translate(lang, 'menu')}"
    what_language_text = translate(lang, "what_language")
    if not what_language_text.strip():
        what_language_text = translate(lang, "default_text")

    await callback.message.edit_text(
        what_language_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translate(lang, "kazakh"), callback_data="kk")],
                [InlineKeyboardButton(text=translate(lang, "russian"), callback_data="ru")],
                [InlineKeyboardButton(text=back_text, callback_data="menu")]
            ]
        )
    )

@language_router.callback_query(lambda callback: callback.data in ["kk", "ru"])
async def set_language_and_check(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data
    await set_language(state, lang_code)
    lang = await get_language(state)

    if update_user_language(callback.from_user.id, lang_code):
        logging.info(f"Language updated for {callback.from_user.id}")
    else:
        logging.warning(f"Failed to update language for {callback.from_user.id}")

    if not check_user_exists(callback.from_user.id):
        text = translate(lang, "employee_not_found")
        await callback.message.edit_text(text)
    else:
        text = translate(lang, "success")
        back_text = f"{translate(lang, 'back')} -> {translate(lang, 'menu')}"
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=back_text, callback_data="menu")]
                ]
            )
        )
