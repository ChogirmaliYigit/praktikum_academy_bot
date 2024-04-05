from aiogram import Router
from aiogram.enums.chat_type import ChatType

from filters import ChatTypeFilter


def setup_routers() -> Router:
    from .users import admin, start, help, register, main
    from .errors import error_handler
    from .groups import start as group_start

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start.router.message.filter(ChatTypeFilter(chat_type=ChatType.PRIVATE))
    group_start.router.message.filter(ChatTypeFilter(chat_type=[ChatType.SUPERGROUP, ChatType.GROUP]))

    router.include_routers(admin.router, start.router, help.router, register.router, main.router,
                           group_start.router, error_handler.router)

    return router
