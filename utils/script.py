from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from utils.text_classes import MainBotStrings
from utils.util_classes import MainForm


async def question(bot: Bot, chat_id: int, state: FSMContext, state_value: State):
    if state_value == MainForm.name.state:
        await bot.send_message(chat_id=chat_id, text=MainBotStrings.nameMessage)
    if state_value == MainForm.silliness.state:
        await bot.send_message(chat_id=chat_id, text=MainBotStrings.sillinessMessage)
    if state_value == MainForm.keywords.state:
        await bot.send_message(chat_id=chat_id, text=MainBotStrings.keywordsMessage)
