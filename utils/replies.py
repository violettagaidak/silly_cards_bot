from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from utils import safe_cast
from utils.script import question
from utils.util_classes import ValidationError


async def variants_message_reply(
        userDataField: str,
        variants: list[str],
        query: types.CallbackQuery,
        state: FSMContext,
        next_state: State
):
    answer_data = query.data
    # chat_id = query.message.chat.id

    if answer_data not in variants:
        await query.answer('Кнопка больше не доступна', show_alert=False)
        return

    # keyboard = InlineKeyboardMarkup()
    answer_text: str = ""
    answer_text = query.message.reply_markup.inline_keyboard[0][0].text
    # for list in query.message.reply_markup.inline_keyboard:
    #     for button in list:
    #         if button.callback_data == query.data:
    #             answer_text = button.text
    #             keyboard.add(InlineKeyboardButton(text=button.text + " ✅", callback_data=answer_data))
    #         else:
    #             keyboard.add(button)

    await state.set_state(next_state)
    await state.update_data({userDataField: answer_text})
    await question(query.bot, query.message.chat.id, state, next_state)
    # await query.answer("Вы выбрали %s" % answer_text, show_alert=False)
    #
    # await query.bot.edit_message_reply_markup(
    #     chat_id=chat_id,
    #     message_id=query.message.message_id,
    #     inline_message_id=query.inline_message_id,
    #     reply_markup=keyboard
    # )


async def text_message_reply(
        text_limit: int,
        user_data_field: str,
        skip_variant: str,
        message: types.Message,
        state: FSMContext,
        next_state: State
):
    text = safe_cast.replaceInvalidCharacters(message.text)

    if skip_variant == text and skip_variant is not None:
        await state.update_data({user_data_field: text})
        await state.set_state(next_state)
        await question(message.bot, message.chat.id, state, next_state)
    elif text:
        if len(text) > text_limit:
            await message.answer(ValidationError.textLimit(len(text), text_limit))
            return

        await state.update_data({user_data_field: text})
        await state.set_state(next_state)
        await question(message.bot, message.chat.id, state, next_state)
    else:
        await message.answer(ValidationError.incorrectAnswerType)
