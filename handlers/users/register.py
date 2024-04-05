from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.states import UserState
from loader import db, bot
from keyboards.inline.buttons import (course_detail_markup, courses_markup, are_you_sure_markup,
                                      back_markup, group_confirmation_markup)
from keyboards.reply.buttons import main_markup
from utils.extra_datas import get_image_url

router = Router()


@router.callback_query(UserState.select_course)
async def select_course(call: types.CallbackQuery, state: FSMContext):
    course_id = int(call.data)
    course = await db.get_course(id=course_id)
    mentor = await db.get_mentor(id=course.get("mentor_id"))
    text = (f"<b>{course.get('title')}</b>\n"
            f"👨‍💻Kursimiz mentori: <b>{mentor.get('full_name')}</b>\n"
            f"ℹ️Kurs haqida: <i>{course.get('description')}</i>\n\n"
            f"💸Kurs narxi: <u>{course.get('price')}</u> so'm")
    markup = await course_detail_markup(course_id, mentor.get("id"))
    if course.get('image'):
        await call.message.delete()
        await call.message.answer_photo(
            photo=await get_image_url(course.get("image")),
            caption=text,
            reply_markup=markup,
        )
    else:
        await call.message.edit_text(text, reply_markup=markup)
    await state.set_state(UserState.course_detail)


@router.callback_query(UserState.course_detail)
async def course_detail_actions(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        text, markup = await courses_markup(await db.select_all_courses())
        await call.message.edit_text(text=f"Qaysi kursda o'qimoqchisiz?\n\n{text}", reply_markup=markup)
        await state.set_state(UserState.select_course)
    else:
        action, _id = call.data.split("_")
        course = await db.get_course(id=int(_id))
        if action == "request":
            user = await db.select_user(telegram_id=call.from_user.id)
            mentor = await db.get_mentor(id=course.get("mentor_id"))
            text = (f"🎓Foydalanuvchi: <a href='tg://user?id={call.from_user.id}'><b>{user.get('full_name')}</b></a>\n"
                    f"📞Telefon raqami: <b>{user.get('phone_number')}</b>\n"
                    f"💻Kurs: <b>{course.get('title')}</b>\n"
                    f"👨‍💻Mentor: <b>{mentor.get('full_name')}</b>\n\n"
                    f"<b><i>Ma'lumotlaringizni tasdiqlaysizmi?</i></b>")
            if course.get("image"):
                await call.message.delete()
                msg = await call.message.answer(text, reply_markup=are_you_sure_markup)
            else:
                msg = await call.message.edit_text(text, reply_markup=are_you_sure_markup)
            await state.set_data({"copy_message_id": msg.message_id, "course_id": course.get("id")})
            await state.set_state(UserState.course_confirmation)
        elif action == "mentor":
            mentor = await db.get_mentor(id=int(_id))
            text = f"👨‍💻Mentorimiz: <b>{mentor.get('full_name')}</b>\n\n<i>{mentor.get('description')}</i>"
            if mentor.get("image"):
                if course.get("image"):
                    await call.message.edit_media(
                        media=types.InputMediaPhoto(
                            media=await get_image_url(mentor.get("image")),
                            caption=text,
                        ),
                        reply_markup=await back_markup(course.get("id")),
                    )
                else:
                    await call.message.delete()
                    await call.message.answer_photo(
                        photo=await get_image_url(mentor.get("image")),
                        caption=text,
                        reply_markup=await back_markup(course.get("id")),
                    )
            else:
                if course.get("image"):
                    await call.message.delete()
                    await call.message.answer(text, reply_markup=await back_markup(course.get("id")))
                else:
                    await call.message.edit_text(text, reply_markup=await back_markup(course.get("id")))
            await state.set_state(UserState.mentor_detail)


@router.callback_query(UserState.course_confirmation)
async def course_confirmation(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        data = await state.get_data()
        user = await db.select_user(telegram_id=call.from_user.id)
        course_student = await db.add_course_student(course_id=data.get("course_id"), student_id=user.get("id"))
        for chat in await db.select_chats():
            await bot.copy_message(
                chat_id=chat.get("chat_id"),
                from_chat_id=call.from_user.id,
                message_id=data.get("copy_message_id"),
                reply_markup=await group_confirmation_markup(course_student.get("id")),
            )
        await call.message.edit_text(
            f"#{course_student.get('id')} raqamli arizangiz adminga yuborildi!✅\nTez orada siz bilan bog'lanamiz😊",
            reply_markup=main_markup,
        )
    else:
        await call.message.edit_text(
            "Ariza yuborish bekor qilindi❌\n\nBotdan qayta foydalanish uchun /start buyrug'ini yuboring.",
            reply_markup=main_markup,
        )
    await state.clear()


@router.callback_query(UserState.mentor_detail)
async def mentor_detail(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("back_"):
        action, course_id = call.data.split("_")
        course_id = int(course_id)
        course = await db.get_course(id=course_id)
        mentor = await db.get_mentor(id=course.get("mentor_id"))
        text = (f"<b>{course.get('title')}</b>\n"
                f"👨‍💻Kursimiz mentori: <b>{mentor.get('full_name')}</b>\n"
                f"ℹ️Kurs haqida: <i>{course.get('description')}</i>\n\n"
                f"💸Kurs narxi: <u>{course.get('price')}</u> so'm")
        markup = await course_detail_markup(course_id, mentor.get("id"))
        if course.get('image'):
            await call.message.delete()
            msg = await call.message.answer_photo(
                photo=await get_image_url(course.get("image")),
                caption=text,
                reply_markup=markup,
            )
        else:
            msg = await call.message.edit_text(text, reply_markup=markup)
        await state.set_data({"copy_message_id": msg.message_id, "course_id": course.get("id")})
        await state.set_state(UserState.course_detail)
