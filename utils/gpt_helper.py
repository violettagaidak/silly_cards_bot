from openai import OpenAI
from dotenv import load_dotenv
from os import environ

load_dotenv()
PROMPT = (
    "Создай поздравительный текст с Новым годом, длиной до 200 символов. "
    "Обязательно используй ключевые слова: %s. Начни текст с обращения к %s. "
    "Определи стиль поздравления по шкале серьезности от 0 до 10, где: "
    "0 — максимально веселое и неформальное, а 10 — строго официальное. "
    "Напиши текст с уровнем серьезности %s."
)


async def create_congratulation(user_data):
    client = OpenAI(api_key=environ['OPENAI_API_KEY'])
    prompt = PROMPT % (user_data.get('keywords'), user_data.get('name'), user_data.get('silliness'))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content
