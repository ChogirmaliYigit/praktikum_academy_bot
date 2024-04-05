import aiohttp
import random
from loader import db
from data import config


escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']


def make_title(title):
    name = ""
    for letter in title:
        if letter in escape_chars:
            name += f'\{letter}'
        else:
            name += letter
    return name


async def generate_sms_code(user_id):
    code = None
    while code is None:
        exist_code = await db.get_code(user_id=user_id)
        if exist_code:
            await db.inactivate_code(user_id)
        generated_code = random.randint(100000, 999999)
        if await db.get_code(code=str(generated_code)):
            continue
        code = generated_code
        await db.add_sms_code(user_id=user_id, code=str(code), is_active=True)
    return str(code)


async def send_sms(phone_number: str, sms: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://rest.smsmode.com/sms/v1/messages",
            data={
                "recipient": {
                    "to": phone_number
                },
                "body": {
                    "text": sms
                }
            },
            headers={"X-Api-Key": ""}
        ) as response:
            print(await response.json())


async def get_image_url(image_path: str):
    backend_url = config.BACKEND_URL[:-1] if config.BACKEND_URL.endswith("/") else config.BACKEND_URL
    return f"{backend_url}/media/{image_path}"
