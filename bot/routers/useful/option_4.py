import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

option_4_router = Router(name="option_4_router")

@option_4_router.callback_query(F.data == "option_4")
async def option_4(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(state)
    name = callback.from_user.full_name
    text = (
        f"{translate(lang, 'option_4').format(name=name)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1. Progress", callback_data="option_progress")],
                [InlineKeyboardButton(text="2. Rocket.chat / Bimoid", callback_data="option_bimoid")],
                [InlineKeyboardButton(text="3. Elma", callback_data="option_elma")],
                [InlineKeyboardButton(text="4. Swapp", callback_data="option_swapp")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="useful_info")]
            ]
        )
    )

def create_router(option_name: str, translation_key: str):
    router = Router(name=f"option_{option_name}")

    @router.callback_query(F.data == f"option_{option_name}")
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
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="option_4")]
                ]
            )
        )

    return router


option_progress = create_router('progress', 'progress')
option_elma = create_router('elma', 'elma')
option_swapp = create_router('swapp', 'swapp')
option_bimoid = create_router('bimoid', 'bimoid')