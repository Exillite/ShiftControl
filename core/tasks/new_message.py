from datetime import datetime, timedelta
import os

from core.celery_app import celery

from core.db.models import Shift, Group, Setting, Employee
from sqlalchemy import select

import asyncio
from core.celery_app import celery
from core.db.database import async_session_factory


from openai import OpenAI

from core.tasks.promt import PROMT

from core.gsheets.sheets_edit import set_shift

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def _create_shift(tg_user_id: int, tg_chat_id: int, tg_message_id: int, message_send_at: datetime, satus: str="need_check", reason=None):
    async with async_session_factory() as session:
        result = await session.execute(select(Employee).where(Employee.tg_id == tg_user_id))
        employee = result.scalar_one_or_none()
        if not employee:
            return

        result = await session.execute(select(Setting).where(Setting.name == "end_work_day"))
        end_work_day = result.scalar_one_or_none()

        end_time = datetime.strptime(end_work_day.value, "%H:%M").time()
        shift_date = message_send_at.date()
        if message_send_at.time() > end_time:
            shift_date += timedelta(days=1)
        message_send_at = message_send_at.replace(tzinfo=None)
        
        result = await session.execute(select(Group).where(Group.tg_chat_id == tg_chat_id))
        group = result.scalar_one_or_none()
        if not group:
            return

        if satus == "ready":
            set_shift(employee.name, shift_date.day, shift_date.month, 1)

        shift = Shift(
            tg_chat_id=tg_chat_id,
            tg_message_id=tg_message_id,
            group_id=group.id,
            message_send_at=message_send_at,
            status=satus,
            reason=reason,
            shift_date=shift_date,
            employee_id=employee.id
        )
        session.add(shift)
        await session.commit()
        await session.refresh(shift)
        return shift

def is_valid_number(s):
    return s.isdigit() and (s == "0" or not s.startswith("0")) and 1 <= int(s) <= 100

@celery.task
def process_new_message(tg_user_id: int, tg_chat_id: int, tg_message_id: int, message_send_at: datetime, message_text: str, message_photo_url: str):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMT + message_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": message_photo_url
                            },
                        },
                    ],
                }
            ],
        )

        answer = response.choices[0].message.content
        score = 0
        if is_valid_number(answer):
            score = int(answer)
        else:
            raise ValueError(f"Invalid response from model: {answer}")


        loop = asyncio.get_event_loop()
        if score >= 40 and score < 70:
            loop.run_until_complete(_create_shift(tg_user_id, tg_chat_id, tg_message_id, message_send_at))
        elif score >= 70:
            loop.run_until_complete(_create_shift(tg_user_id, tg_chat_id, tg_message_id, message_send_at, satus="ready", reason="bot"))
        else:
            return
    except Exception as e:
        print(f"Error processing new message: {e}")