from typing import Tuple, Union
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import db

inline_keyboard = [[
    InlineKeyboardButton(text="✅ Ha", callback_data='yes'),
    InlineKeyboardButton(text="❌ Yo'q", callback_data='no')
]]
are_you_sure_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def courses_markup(courses, view_field: str = "title") -> Tuple[str, InlineKeyboardMarkup]:
    keyboard = []
    text = ""
    cnt = 1
    for course in courses[::2]:
        row = [
            InlineKeyboardButton(text=str(cnt), callback_data=str(course.get("id")))
        ]
        text += f"{cnt}. <b>{course.get(view_field)}</b>\n"

        try:
            course = courses[int(courses.index(course)) + 1]
            row.append(InlineKeyboardButton(text=str(cnt + 1), callback_data=str(course.get("id"))))
            text += f"{cnt + 1}. <b>{course.get(view_field)}</b>\n"
        except (IndexError, AttributeError):
            pass
        keyboard.append(row)
        cnt += 2
    return text, InlineKeyboardMarkup(inline_keyboard=keyboard)


async def did_not_get_code() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Kodni olmadingizmi?", callback_data="not_get"),
            ],
        ],
    )


async def course_detail_markup(course_id: int, mentor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Kursga yozilish➕", callback_data=f"request_{course_id}"),
            ],
            [
                InlineKeyboardButton(text="Mentor haqida bilish👨‍💻", callback_data=f"mentor_{mentor_id}"),
            ],
            [
                InlineKeyboardButton(text="⬅️Orqaga", callback_data="back"),
            ],
        ],
    )


async def back_markup(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️Orqaga", callback_data=f"back_{course_id}"),
            ],
        ],
    )


async def group_confirmation_markup(course_student_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Tasdiqlash✅", callback_data=f"confirm_{course_student_id}"),
                InlineKeyboardButton(text="Bekor qilish❌", callback_data=f"cancel_{course_student_id}"),
            ],
        ],
    )


async def my_requests_markup(requests, index: int = 0) -> Tuple[str, Union[InlineKeyboardMarkup, None]]:
    try:
        request = requests[index]
    except IndexError:
        return "", None

    user = await db.select_user(id=request.get("student_id"))
    statuses = {
        "requested": "So'rov yuborilgan🔄",
        "canceled": "Bekor qilingan❌",
        "accepted": "Tasdiqlangan✅",
        "studying": "O'qimoqda👨‍🏫",
    }

    course = await db.get_course(id=request.get("course_id"))
    mentor = await db.get_mentor(id=course.get("mentor_id"))

    text = f"#{request.get('id')} raqamli arizangiz\n\n"\
           f"🎓Foydalanuvchi: <b>{user.get('full_name')}</b>\n"\
           f"📞Telefon raqami: <b>{user.get('phone_number')}</b>\n"\
           f"💻Kurs: <b>{course.get('title')}</b>\n"\
           f"👨‍💻Mentor: <b>{mentor.get('full_name')}</b>\n\n"\
           f"{statuses.get(request.get('status'))}"

    pagination_keyboard = []
    if requests[:index]:
        pagination_keyboard.append(InlineKeyboardButton(text="⬅️", callback_data=f"previous_{index - 1}"))
    if requests[index+1:]:
        pagination_keyboard.append(InlineKeyboardButton(text="➡️", callback_data=f"next_{index + 1}"))

    return text, InlineKeyboardMarkup(inline_keyboard=[pagination_keyboard])
