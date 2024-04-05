from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram.exceptions import TelegramBadRequest
from loader import db, bot

router = Router()


@router.message(CommandStart())
async def group_start(message: types.Message):
    try:
        await message.reply("Shu yerdaman!")
        chat_id = message.chat.id
        await db.add_chat(chat_id=chat_id)
        print(f"New chat added: {chat_id}")
    except TelegramBadRequest as error:
        print(error)


@router.callback_query()
async def course_student_detail(call: types.CallbackQuery):
    if call.data.startswith("confirm_") or call.data.startswith("cancel_"):
        action, _id = call.data.split("_")
        _id = int(_id)
        course_student = await db.get_course_student(_id)
        status = "accepted" if action == "confirm" else "canceled"
        await db.update_course_student_status(
            status=status,
            course_id=course_student.get("course_id"),
            student_id=course_student.get("student_id"),
        )
        course = await db.get_course(id=course_student.get("course_id"))
        mentor = await db.get_mentor(id=course.get("mentor_id"))

        statuses = {
            "accepted": "Tasdiqlangan✅",
            "canceled": "Bekor qilingan❌",
        }

        user = await db.select_user(id=course_student.get("student_id"))

        await call.message.edit_text(
            text=(f"🎓Foydalanuvchi: <b>{user.get('full_name')}</b>\n"
                  f"📞Telefon raqami: <b>{user.get('phone_number')}</b>\n"
                  f"💻Kurs: <b>{course.get('title')}</b>\n"
                  f"👨‍💻Mentor: <b>{mentor.get('full_name')}</b>\n\n"
                  f"{statuses.get(status)}"),
        )

        if action == "confirm":
            await bot.send_message(
                chat_id=user.get("telegram_id"),
                text=f"Sizning #{course_student.get('id')} raqamli arizangiz qabul qilindi🥳"
            )
        else:
            await bot.send_message(
                chat_id=user.get("telegram_id"),
                text=f"Sizning #{course_student.get('id')} raqamli arizangiz bekor qilindi😔"
            )
