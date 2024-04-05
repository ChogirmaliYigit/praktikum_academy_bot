from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, telegram_id, phone_number, verified=False):
        sql = "INSERT INTO telegram_users (full_name, telegram_id, phone_number, verified) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, telegram_id, phone_number, verified, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM telegram_users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM telegram_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM telegram_users"
        return await self.execute(sql, fetchval=True)

    async def update_user_phone_number(self, phone_number, telegram_id):
        sql = "UPDATE telegram_users SET phone_number=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone_number, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM telegram_users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE telegram_users", execute=True)

    async def select_all_courses(self):
        sql = "SELECT * FROM courses"
        return await self.execute(sql, fetch=True)

    async def select_all_mentors(self):
        sql = "SELECT * FROM mentors"
        return await self.execute(sql, fetch=True)

    async def get_course(self, **kwargs):
        sql = "SELECT * FROM courses WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def get_mentor(self, **kwargs):
        sql = "SELECT * FROM mentors WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_sms_code(self, user_id, code, is_active=True):
        sql = "INSERT INTO sms_verifications (user_id, code, is_active) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, user_id, code, is_active, fetchrow=True)

    async def get_code(self, **kwargs):
        sql = "SELECT * FROM sms_verifications WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        sql += " AND is_active = True"
        return await self.execute(sql, *parameters, fetchrow=True)

    async def inactivate_code(self, user_id):
        sql = "UPDATE sms_verifications SET is_active = False WHERE user_id = $1"
        return await self.execute(sql, user_id, execute=True)

    async def make_user_verified(self, _id):
        sql = "UPDATE telegram_users SET verified = True WHERE id = $1"
        return await self.execute(sql, _id, execute=True)

    async def add_course_student(self, course_id: int, student_id: int, status: str = "requested"):
        sql = "INSERT INTO course_students (course_id, student_id, status) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, course_id, student_id, status, fetchrow=True)

    async def add_chat(self, chat_id: int):
        sql = "INSERT INTO chats (chat_id) VALUES ($1) RETURNING *"
        return await self.execute(sql, chat_id, fetchrow=True)

    async def get_chat(self, **kwargs):
        sql = "SELECT * FROM chats WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_chats(self):
        sql = "SELECT * FROM chats"
        return await self.execute(sql, fetch=True)

    async def update_course_student_status(self, status: str, course_id: int, student_id: int):
        sql = "UPDATE course_students SET status = $1 WHERE course_id = $2 AND student_id = $3"
        return await self.execute(sql, status, course_id, student_id, execute=True)

    async def get_course_student(self, _id: int):
        sql = "SELECT * FROM course_students WHERE id = $1"
        return await self.execute(sql, _id, fetchrow=True)

    async def select_course_students(self):
        sql = "SELECT * FROM course_students"
        return await self.execute(sql, fetch=True)
