from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


phone_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Telefon raqamini ulashish 📱",
                request_contact=True,
            ),
        ],
    ],
)


main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💻Kurslar haqida"),
            KeyboardButton(text="👨‍💻Mentorlar haqida"),
        ],
        [
            KeyboardButton(text="📝Arizalarim"),
            KeyboardButton(text="📞Telefon raqamini o'zgartirish"),
        ]
    ],
)
