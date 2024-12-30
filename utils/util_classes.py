from aiogram.fsm.state import State, StatesGroup


class BotConfig:
    def __init__(
            self,
            token: str,
            # payment_token: str,
            heroku_app_name: str,
    ):
        self.token = token
        # self.payment_token = payment_token
        self.heroku_app_name = heroku_app_name
        self.webhook_host = f'https://{heroku_app_name}.herokuapp.com'
        self.webhook_path = f'/webhook/{token}'
        self.webhook_url = f'{self.webhook_host}{self.webhook_path}'


class MainForm(StatesGroup):
    start = State()
    help = State()
    cancel = State()

    name = State()
    holiday = State()
    silliness = State()
    silliness_error = State()

    keywords = State()
    keywords_error = State()

    waiting = State()
    result = State()


class AnswerField:
    name = "name"
    holiday = "holiday"
    silliness = "silliness"
    keywords = "keywords"


class ValidationError:
    incorrectAnswerType = "Повторите попытку - неправильное сообщение!"
    def textLimit(messageLenght: int, limit: int) -> str:
        return "Пожалуйста, сделай текст чуть короче — не более %s символов. Сейчас длина текста %s символов." % (
            limit, messageLenght)
