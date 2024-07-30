import logging
from aiogram.fsm.context import FSMContext
from bot.lang.kk import kk
from bot.lang.ru import ru

translations = {
    "kk": kk,
    "ru": ru
}


def translate(lang, key) -> str:
    translation = translations.get(lang, {}).get(key, "")
    print(translation)
    return translation


async def get_language(state: FSMContext):
    state_data = await state.get_data()
    return state_data.get("language", "kk")


async def set_language(state: FSMContext, language: str) -> str:
    await state.update_data(language=language)
    success_text = translate(language, "success")
    logging.info(f"Set language success text: {success_text}")
    return success_text
