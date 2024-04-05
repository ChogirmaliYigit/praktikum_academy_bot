from aiogram.filters.state import StatesGroup, State


class UserState(StatesGroup):
    send_verification_code = State()
    check_code = State()
    select_course = State()
    course_detail = State()
    course_confirmation = State()
    mentor_detail = State()
    select_mentor = State()
    my_requests = State()


class AdminState(StatesGroup):
    are_you_sure = State()
    ask_ad_content = State()
