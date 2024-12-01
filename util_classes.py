from aiogram.fsm.state import State, StatesGroup


class BotConfig:
    def __init__(
            self,
            token: str,
            payment_token: str,
            heroku_app_name: str,
    ):
        self.token = token
        self.payment_token = payment_token
        self.heroku_app_name = heroku_app_name
        self.webhook_host = f'https://{heroku_app_name}.amvera.io'  #todo change to heroku
        self.webhook_path = f'/webhook/{token}'
        self.webhook_url = f'{self.webhook_host}{self.webhook_path}'


class MainState(StatesGroup):
    start = State()
    end = State()
