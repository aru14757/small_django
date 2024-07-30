import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

def create_router(option_number: int, translation_key: str):
    router = Router(name=f"option_{option_number}_router")

    @router.callback_query(F.data == f"option_{option_number}")
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
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="useful_info")]
                ]
            )
        )

    return router


option_1_router = create_router(1, 'address')
option_2_router = create_router(2, 'glossary')
option_5_router = create_router(5, 'documents')
option_6_router = create_router(6, 'option_6')
option_7_router = create_router(7, 'option_7')
option_8_router = create_router(8, 'option_8')
