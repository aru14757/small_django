import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

choice_9_router = Router(name="choice_9_router")

@choice_9_router.callback_query(F.data == "choice_9")
async def choice_5(callback: CallbackQuery, state: FSMContext):
    logging.info("Callback received for choice_9")
    lang = await get_language(state)
    name = callback.from_user.full_name
    text = (
        f"{translate(lang, 'choice_9').format(name=name)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="choice_9_1")],
                [InlineKeyboardButton(text="2", callback_data="choice_9_2")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="option_3")]
            ]
        )
    )



def create_router(choice_name: int, translation_key: str):
    router = Router(name=f"choice_9_{choice_name}_router")

    @router.callback_query(F.data == f"choice_9_{choice_name}")
    async def handle_callback(callback: CallbackQuery, state: FSMContext):
        logging.info(f"Callback received for choice_9_{choice_name}")
        lang = await get_language(state)
        name = callback.from_user.full_name
        text = (
            f"{translate(lang, translation_key).format(name=name)}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="choice_9")]
                ]
            )
        )

    return router

choice_9_1 = create_router(1, 'choice_9_1')
choice_9_2 = create_router(2, 'choice_9_2')