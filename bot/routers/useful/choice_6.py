import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.lang import translate, get_language

logging.basicConfig(level=logging.INFO)

choice_6_router = Router(name="choice_6_router")

@choice_6_router.callback_query(F.data == "choice_6")
async def choice_6(callback: CallbackQuery, state: FSMContext):
    logging.info("Callback received for choice_6")
    lang = await get_language(state)
    name = callback.from_user.full_name
    text = (
        f"{translate(lang, 'choice_6').format(name=name)}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="choice_6_1")],
                [InlineKeyboardButton(text="2", callback_data="choice_6_2")],
                [InlineKeyboardButton(text="3", callback_data="choice_6_3")],
                [InlineKeyboardButton(text="4", callback_data="choice_6_4")],
                [InlineKeyboardButton(text=translate(lang, "back"), callback_data="option_3")]
            ]
        )
    )



def create_router(choice_name: int, translation_key: str):
    router = Router(name=f"choice_6_{choice_name}_router")

    @router.callback_query(F.data == f"choice_6_{choice_name}")
    async def handle_callback(callback: CallbackQuery, state: FSMContext):
        logging.info(f"Callback received for choice_6_{choice_name}")
        lang = await get_language(state)
        name = callback.from_user.full_name
        text = (
            f"{translate(lang, translation_key).format(name=name)}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=translate(lang, "back"), callback_data="choice_6")]
                ]
            )
        )

    return router

choice_6_1 = create_router(1, 'choice_6_1')
choice_6_2 = create_router(2, 'choice_6_2')
choice_6_3 = create_router(3, 'choice_6_3')
choice_6_4 = create_router(4, 'choice_6_4')