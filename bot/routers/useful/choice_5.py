import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

choice_5_router = Router(name="choice_5_router")

@choice_5_router.callback_query(F.data == "choice_5")
async def choice_5(callback: CallbackQuery, state: FSMContext):
    logging.info("Callback received for choice_5")
    lang = await get_language(state)
    name = callback.from_user.full_name
    text = (
        f"{translate(lang, 'choice_5').format(name=name)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="choice_5_1")],
                [InlineKeyboardButton(text="2", callback_data="choice_5_2")],
                [InlineKeyboardButton(text="3", callback_data="choice_5_3")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="option_3")]
            ]
        )
    )



def create_router(choice_name: int, translation_key: str):
    router = Router(name=f"choice_5_{choice_name}_router")

    @router.callback_query(F.data == f"choice_5_{choice_name}")
    async def handle_callback(callback: CallbackQuery, state: FSMContext):
        logging.info(f"Callback received for choice_5_{choice_name}")
        lang = await get_language(state)
        name = callback.from_user.full_name
        text = (
            f"{translate(lang, translation_key).format(name=name)}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="choice_5")]
                ]
            )
        )

    return router

choice_5_1 = create_router(1, 'choice_5_1')
choice_5_2 = create_router(2, 'choice_5_2')
choice_5_3 = create_router(3, 'choice_5_3')