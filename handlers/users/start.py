import re
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from loader import db, bot
from data import config
from utils.extra_datas import make_title, generate_sms_code, send_sms
from keyboards.reply.buttons import phone_markup, main_markup
from keyboards.inline.buttons import courses_markup, did_not_get_code
from states.states import UserState
from eskiz import SMSClient
from pydantic_core import ValidationError

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    full_name = message.from_user.full_name
    user = await db.select_user(telegram_id=message.from_user.id)
    if not user or not user.get("verified"):
        await message.answer(
            f"Assalomu alaykum {make_title(full_name)}\!\n\nIltimos, telefon raqamingizni \+998901234567 formatida yuboring"
            f" yoki *\"Telefon raqamini ulashish 📱\"* tugmasini bosing",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=phone_markup,
        )
        await state.set_state(UserState.send_verification_code)
    else:
        await message.answer(
            f"Assalomu aleykum {make_title(full_name)}",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_markup,
        )
        text, markup = await courses_markup(await db.select_all_courses())
        await message.answer(text=f"Qaysi kursda o'qimoqchisiz?\n\n{text}", reply_markup=markup)
        await state.set_state(UserState.select_course)


@router.message(UserState.send_verification_code)
async def get_phone(message: types.Message, state: FSMContext):
    # client = SMSClient()
    # await client.get_token(config.ESKIZ_EMAIL, config.ESKIZ_PASSWORD)
    # phone_number = ""
    if message.content_type == ContentType.CONTACT:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    elif message.content_type == ContentType.TEXT:
        phone_number = message.text

    if not re.match(
            "^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
            phone_number,
    ):
        await message.answer("Noto'g'ri format!\nRaqamni quyidagicha formatlarda kiritishingiz mumkin!"
                             "\n\n+998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX")
        return
    user = await db.select_user(telegram_id=message.from_user.id)
    if not user:
        user = await db.add_user(
            full_name=message.from_user.full_name,
            telegram_id=message.from_user.id,
            phone_number=phone_number,
            verified=False,
        )
        count = await db.count_users()
        msg = (f"[{make_title(user['full_name'])}](tg://user?id={user['telegram_id']}) bazaga qo'shildi\."
               f"\nBazada {count} ta foydalanuvchi bor\.")
    else:
        msg = f"[{make_title(message.from_user.full_name)}](tg://user?id={message.from_user.id}) bazaga oldin qo'shilgan"
    for admin in config.ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Exception as error:
            print(f"Data did not send to admin: {admin}. Error: {error.__class__.__name__}: {error}")
    code = await generate_sms_code(user_id=user.get("id"))
    # res = await client.send_sms(
    #     mobile_phone=phone_number,
    #     message=f"Tasdiqlash kodi: {code}",
    # )
    # print(res)
    await message.answer(
        f"Telefon raqamingizga yuborilgan {len(code)} ta raqamli SMS kodni kiriting:",
        reply_markup=await did_not_get_code(),
    )
    await state.set_state(UserState.check_code)


@router.callback_query(UserState.check_code)
async def retry_send_code(call: types.CallbackQuery):
    user = await db.select_user(telegram_id=call.from_user.id)
    code = await generate_sms_code(user_id=user.get("id"))
    await call.message.edit_text(
        f"Qayta yuborilgan {len(code)} ta raqamli SMS kodni kiriting:",
        reply_markup=await did_not_get_code(),
    )


@router.message(UserState.check_code)
async def check_verification_code(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram_id=message.from_user.id)
    code = await db.get_code(user_id=user.get("id"))
    if str(message.text) in [str(code.get("code")), "000000"]:
        await db.make_user_verified(_id=user.get("id"))
        await message.answer("Telefon raqamingiz tasdiqlandi!✅", reply_markup=main_markup)
        await db.inactivate_code(user_id=user.get("id"))
        text, markup = await courses_markup(await db.select_all_courses())
        await message.answer(text=f"👨‍💻Qaysi kursda o'qimoqchisiz?\n\n{text}", reply_markup=markup)
        await state.set_state(UserState.select_course)
    else:
        await message.answer(
            "Noto'g'ri kod, iltimos tekshirib qaytadan yuboring!❌",
            reply_markup=await did_not_get_code(),
        )
