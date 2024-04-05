from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from states.states import UserState
from keyboards.inline.buttons import courses_markup, back_markup, my_requests_markup
from keyboards.reply.buttons import phone_markup
from utils.extra_datas import get_image_url
from loader import db


router = Router()


@router.message(F.text == "💻Kurslar haqida")
async def courses(message: types.Message, state: FSMContext):
    text, markup = await courses_markup(await db.select_all_courses())
    await message.answer(text=f"Qaysi kursda o'qimoqchisiz?\n\n{text}", reply_markup=markup)
    await state.set_state(UserState.select_course)


@router.message(F.text == "👨‍💻Mentorlar haqida")
async def mentors(message: types.Message, state: FSMContext):
    text, markup = await courses_markup(await db.select_all_mentors(), view_field="full_name")
    await message.answer(text=f"Mentorni tanlang 1\n\n{text}", reply_markup=markup)
    await state.set_state(UserState.select_mentor)


@router.callback_query(UserState.select_mentor)
async def select_mentor_(call: types.CallbackQuery):
    if call.data.startswith("back_"):
        mentor = await db.get_mentor(id=int(call.data.split("_")[-1]))
        text, markup = await courses_markup(await db.select_all_mentors(), view_field="full_name")
        if mentor.get("image"):
            await call.message.delete()
            await call.message.answer(text=f"Mentorni tanlang\n\n{text}", reply_markup=markup)
        else:
            await call.message.edit_text(f"Mentorni tanlang\n\n{text}", reply_markup=markup)
    else:
        mentor = await db.get_mentor(id=int(call.data))
        text = f"👨‍💻Mentorimiz: <b>{mentor.get('full_name')}</b>\n\n<i>{mentor.get('description')}</i>"
        if mentor.get("image"):
            await call.message.delete()
            await call.message.answer_photo(
                photo=await get_image_url(mentor.get("image")),
                caption=text,
                reply_markup=await back_markup(mentor.get("id")),
            )
        else:
            await call.message.edit_text(text, reply_markup=await back_markup(mentor.get("id")))


@router.message(F.text == "📝Arizalarim")
async def requests(message: types.Message, state: FSMContext):
    text, markup = await my_requests_markup(await db.select_course_students())
    if text and markup:
        await message.answer(text=text, reply_markup=markup)
        await state.set_state(UserState.my_requests)
    else:
        await message.answer("<b>Sizda faol arizalar mavjud emas</b>")


@router.callback_query(UserState.my_requests)
async def requests_pagination(call: types.CallbackQuery):
    if call.data.startswith("next_") or call.data.startswith("previous_"):
        action, index = call.data.split("_")
        text, markup = await my_requests_markup(await db.select_course_students(), index=int(index))
        if text and markup:
            await call.message.edit_text(text, reply_markup=markup)


@router.message(F.text == "📞Telefon raqamini o'zgartirish")
async def phone_number(message: types.Message, state: FSMContext):
    await message.answer(
        "Iltimos, telefon raqamingizni \+998901234567 formatida yuboring "
        "yoki *\"Telefon raqamini ulashish 📱\"* tugmasini bosing",
        reply_markup=phone_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await state.set_state(UserState.send_verification_code)
