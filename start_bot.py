import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram import Router
from aiogram.filters import Command

from utils.util_classes import BotConfig, MainState

current_config = BotConfig(
    token="8065725480:AAE2mnYl6U4JPS2Gbu62kYWDptiCpWXcQaE",
    payment_token="",
    heroku_app_name=""
)

bot = Bot(token=current_config.token)
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)
dp.include_router(router)


async def default_start(bot: Bot, chat_id: int, user_id: int, state: FSMContext):
    await state.set_state(MainState.start)


async def start(message: types.Message, state: FSMContext):
    await default_start(message.bot, message.chat.id, message.from_user.id, state)


async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Пока!', reply_markup=ReplyKeyboardRemove()
    )


async def help(message: types.Message, state: FSMContext):
    await message.answer(
        'ПОМОГИТЕ!', reply_markup=ReplyKeyboardRemove()
    )


def register_handlers(router: Router):
    router.message.register(start, Command(commands=["start"]))
    router.message.register(cancel, Command(commands=["cancel"]))
    router.message.register(help, Command(commands=["help"]))


async def main():
    register_handlers(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
