import asyncio
from os import environ, getenv

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router, types, Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiohttp import web
from aiogram.types import BotCommand
from aiogram.fsm.state import State
from dotenv import load_dotenv
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


from utils.replies import text_message_reply, variants_message_reply
from utils.util_classes import AnswerField, BotConfig, MainForm
from utils.text_classes import MainBotStrings
from utils.util_functions import is_int_between_0_and_10, is_less_5_words
from aiogram.exceptions import TelegramBadRequest
from utils.gpt_helper import create_congratulation

TEXT_LIMIT = 120
load_dotenv()

current_config = BotConfig(
    token=environ['BOT_TOKEN'],
    # payment_token="",
    heroku_app_name="silly-greetings-f554daa29fb8"
)

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(getenv('PORT', default=8000))
WEBHOOK_PATH = f"/webhook/{current_config.token}"

print(environ['BOT_TOKEN'])
print(WEBAPP_PORT)

bot = Bot(token=current_config.token)
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)
dp.include_router(router)


async def start(message: types.Message, state: FSMContext):
    bot = message.bot
    await state.set_state(MainForm.start)
    ok_button = InlineKeyboardButton(text="Погнали!", callback_data='okay')
    inline_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[ok_button]])
    await bot.send_message(message.chat.id, MainBotStrings.helloMessage, reply_markup=ReplyKeyboardRemove())
    await bot.send_message(text=MainBotStrings.hello2Message, reply_markup=inline_kb, chat_id=message.chat.id)


async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Пока!', reply_markup=ReplyKeyboardRemove()
    )


async def help(message: types.Message, state: FSMContext):
    await message.answer(
        'ПОМОГИТЕ!', reply_markup=ReplyKeyboardRemove()
    )


async def name_reply(message: types.Message, state: FSMContext, next_state: State):
    await text_message_reply(
        TEXT_LIMIT,
        AnswerField.name,
        '',
        message,
        state,
        next_state
    )


async def name_reply_silliness(message: types.Message, state: FSMContext):
    await name_reply(message, state, MainForm.silliness)
    await state.set_state(MainForm.silliness)


async def silliness_reply(message: types.Message, state: FSMContext, next_state: State):
    if is_int_between_0_and_10(message.text):
        await text_message_reply(
            TEXT_LIMIT,
            AnswerField.silliness,
            '',
            message,
            state,
            next_state
        )
        await state.set_state(next_state)
    else:
        # If the input is invalid, send an error message and reset the state to silliness
        await silliness_reply_error(message, state)


async def silliness_reply_keywords(message: types.Message, state: FSMContext):
    await silliness_reply(message, state, MainForm.keywords)


async def silliness_reply_error(message: types.Message, state: FSMContext):
    # Send error message
    await message.answer(MainBotStrings.sillinessErrorMessage, reply_markup=ReplyKeyboardRemove())
    # Reset the state to silliness
    await state.set_state(MainForm.silliness)
    # Prompt the user again
    await message.answer(MainBotStrings.sillinessMessage, reply_markup=ReplyKeyboardRemove())


async def keywords_reply(message: types.Message, state: FSMContext, next_state: State):
    if is_less_5_words(message.text):
        await state.update_data(keywords=message.text)  # Save the keywords in FSMContext
        await state.set_state(MainForm.result)

        # Retrieve user data and generate the result
        user_data = await state.get_data()
        await message.answer(MainBotStrings.waitingMessage, reply_markup=ReplyKeyboardRemove())
        result = await create_congratulation(user_data)

        # Create the inline keyboard with buttons
        buttons = [
            [InlineKeyboardButton(text="Мне нравится", callback_data="good")],
            [InlineKeyboardButton(text="Хочу сгенерировать ещё раз", callback_data="again")],
            [InlineKeyboardButton(text="Начать сначала", callback_data="restart")]
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Delete previous result message with buttons if exists
        previous_message_id = user_data.get("last_result_message_id")
        if previous_message_id:
            try:
                await message.bot.delete_message(message.chat.id, previous_message_id)
            except TelegramBadRequest:
                pass  # Ignore if the message can't be deleted (e.g., due to Telegram limitations)

        # Send the new result message with buttons
        sent_message = await message.answer(MainBotStrings.resultMessage % result, reply_markup=inline_kb)

        # Save the new message_id in the FSMContext
        await state.update_data(last_result_message_id=sent_message.message_id)
    else:
        # If the input is invalid, send an error message
        await keywords_reply_error(message, state)


async def keywords_reply_waiting(message: types.Message, state: FSMContext):
    await keywords_reply(message, state, MainForm.waiting)


async def keywords_reply_error(message: types.Message, state: FSMContext):
    # Send error message
    await message.answer(MainBotStrings.keywordsErrorMessage, reply_markup=ReplyKeyboardRemove())
    # Reset the state to silliness
    await state.set_state(MainForm.keywords)
    # Prompt the user again
    await message.answer(MainBotStrings.keywordsMessage, reply_markup=ReplyKeyboardRemove())


async def start_reply(query: types.CallbackQuery, state: FSMContext, next_state: State):
    await variants_message_reply(
        'start',
        ['okay'],
        query,
        state,
        next_state
    )
    await query.answer()  # Acknowledge the callback query


async def start_reply_name(query: types.CallbackQuery, state: FSMContext):
    await start_reply(query, state, MainForm.name)


# Handle button clicks
async def handle_result_buttons(query: types.CallbackQuery, state: FSMContext):
    # Retrieve the message_id of the last result message
    user_data = await state.get_data()
    last_message_id = user_data.get("last_result_message_id")

    # Allow button clicks only on the last message
    if query.message.message_id != last_message_id:
        await query.answer("This action is no longer available.", show_alert=True)
        return

    if query.data == "good":
        # Send "Bye!" message and clear the state
        await query.message.answer(MainBotStrings.endMessage, reply_markup=ReplyKeyboardRemove())
        await state.clear()

    elif query.data == "again":
        # Check the click limit
        again_clicks = user_data.get("again_clicks", 0)
        if again_clicks >= 5:
            await query.message.answer(
                "Перегенировать поздравление можно только 5 раз. Перезапустите бот с помощью команды /start.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

        # Increment the click counter
        again_clicks += 1
        await state.update_data(again_clicks=again_clicks)

        # Rerun the create_congratulation and display the result
        await query.message.answer(MainBotStrings.waitingMessage, reply_markup=ReplyKeyboardRemove())
        result = await create_congratulation(user_data)
        buttons = [
            [InlineKeyboardButton(text="Мне нравится", callback_data="good")],
            [InlineKeyboardButton(text="Хочу сгенерировать ещё раз", callback_data="again")],
            [InlineKeyboardButton(text="Начать сначала", callback_data="restart")]
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        sent_message = await query.message.answer(MainBotStrings.resultMessage % result, reply_markup=inline_kb)

        # Update the last_result_message_id
        await state.update_data(last_result_message_id=sent_message.message_id)

    elif query.data == "restart":
        # Reset the click counter and trigger the start function
        await state.update_data(again_clicks=0)  # Reset the counter
        await start(query.message, state)

    await query.answer()  # Acknowledge the callback query


# Register Handlers
def register_handlers(router: Router):
    # Register general commands
    router.message.register(start, Command(commands=["start"]))
    router.message.register(cancel, Command(commands=["cancel"]))
    router.message.register(help, Command(commands=["help"]))

    # Register callback query handlers
    router.callback_query.register(start_reply_name, lambda cb: cb.data == 'okay')
    router.callback_query.register(handle_result_buttons, lambda cb: cb.data in ["good", "again", "restart"])

    # Register state-specific handlers using StateFilter
    router.message.register(name_reply_silliness, StateFilter(MainForm.name))

    router.message.register(silliness_reply_keywords, StateFilter(MainForm.silliness))
    router.message.register(silliness_reply_error, StateFilter(MainForm.silliness_error))

    router.message.register(keywords_reply_waiting, StateFilter(MainForm.keywords))
    router.message.register(keywords_reply_error, StateFilter(MainForm.keywords_error))


async def on_startup(bot: Bot):
    # Set default commands (optional)
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot")
    ])
    # Set the webhook URL
    webhook_url = f"https://{current_config.heroku_app_name}.herokuapp.com{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)
    print(f"Webhook set to: {webhook_url}")


async def on_shutdown(bot: Bot):
    # Gracefully shutdown webhook and close bot session
    await bot.delete_webhook()
    await bot.session.close()


def main():
    # Register all handlers
    register_handlers(router)
    if not current_config.heroku_app_name:
        # Run in polling mode
        asyncio.run(dp.start_polling(bot, skip_updates=True))
    else:
        # Run in webhook mode
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # Start the web application
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    main()
