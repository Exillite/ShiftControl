from datetime import datetime
import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select
from core.db.database import engine, async_session_factory
from core.db.base import Base

from core.db.models import *

from core.celery_app import celery
from core.gsheets.sheets_edit import set_shift, add_employee
from core.tasks.new_message import process_new_message

import httpx


BOT_TOKEN = os.getenv("BOT_TOKEN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await ensure_default_settings()

    yield

    # shutdown
    # await engine.dispose()


async def ensure_default_settings():
    defaults = {
        "end_work_day": "23:00"
    }

    async with async_session_factory() as session:
        for name, value in defaults.items():
            result = await session.execute(select(Setting).where(Setting.name == name))
            existing = result.scalar_one_or_none()
            if not existing:
                session.add(Setting(name=name, value=value))
        await session.commit()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "OK"}


class NewMessage(BaseModel):
    tg_user_id: int
    tg_chat_id: int
    tg_message_id: int
    message_send_at: datetime
    message_text: str
    message_file_id: str


# @app.post("/new_message")
# async def new_message(data: NewMessage):
#     try:
#         process_new_message.delay(
#             tg_user_id=data.tg_user_id,
#             tg_chat_id=data.tg_chat_id, 
#             tg_message_id=data.tg_message_id,
#             message_send_at=data.message_send_at,
#             message_text=data.message_text,
#             message_file_id=data.message_file_id
#         )

#         return {"status": "ok"}
#     except Exception as e:
#         print(f"Error processing message: {e}")



class NewGroup(BaseModel):
    tg_chat_id: int


@app.post("/new_group")
async def new_group(data: NewGroup):
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Group).where(Group.tg_chat_id == data.tg_chat_id))
            existing = result.scalar_one_or_none()
            if existing:
                return {"status": "ok", "message": "Group already exists"}

            group = Group(tg_chat_id=data.tg_chat_id, object_id=None)
            session.add(group)
            await session.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing new group: {e}")


async def get_chat_info(chat_id: int):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"chat_id": chat_id})

    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Telegram API error: {data.get('description')}")
    
    chat = data["result"]

    title = chat.get("title") or chat.get("first_name") or chat.get("username") or "Unknown"

    photo = chat.get("photo")
    avatar_url = None

    if photo:
        file_id = photo.get("small_file_id") or photo.get("big_file_id")
        if file_id:
            avatar_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_id}"
        
    return {
        "chat_id": chat_id,
        "title": title,
        "avatar_url": avatar_url
    }

@app.get("/chat_info/{chat_id}")
async def chat_info(chat_id: int):
    try:
        info = await get_chat_info(chat_id)
        return {"status": "ok", "data": info}
    except Exception as e:
        print(f"Error fetching chat info: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/groups")
async def list_groups():
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Group))
            groups = result.scalars().all()
            
            data = []
            for group in groups:
                data.append({
                    "id": group.id,
                    "tg_chat_id": group.tg_chat_id,

                })
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error listing groups: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/group")
async def get_group(group_id: int):
    try:
        async with async_session_factory() as session:
            group = await session.get(Group, group_id)
            if not group:
                return {"status": "error", "message": "Group not found"}
            data = {
                "id": group.id,
                "tg_chat_id": group.tg_chat_id,
                "object_id": group.object_id
            }
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error fetching group: {e}")
        return {"status": "error", "message": str(e)}


class NewObject(BaseModel):
    name: str

@app.post("/new_object")
async def new_object(data: NewObject):
    try:
        async with async_session_factory() as session:
            obj = Object(name=data.name)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return {"status": "ok", "data": {"id": obj.id, "name": obj.name}}
    except Exception as e:
        print(f"Error creating new object: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/objects")
async def list_objects():
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Object))
            objects = result.scalars().all()
            data = [{"id": obj.id, "name": obj.name} for obj in objects]
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error listing objects: {e}")
        return {"status": "error", "message": str(e)}

class AssignGroupToObject(BaseModel):
    group_id: int
    object_id: int

@app.post("/assign_group_to_object")
async def assign_group_to_object(data: AssignGroupToObject):
    try:
        async with async_session_factory() as session:
            group = await session.get(Group, data.group_id)
            if not group:
                return {"status": "error", "message": "Group not found"}

            obj = await session.get(Object, data.object_id)
            if not obj:
                return {"status": "error", "message": "Object not found"}

            group.object_id = obj.id
            await session.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error assigning group to object: {e}")
        return {"status": "error", "message": str(e)}


class NewEmployee(BaseModel):
    name: str
    tg_id: int

@app.post("/new_employee")
async def new_employee(data: NewEmployee):
    try:
        async with async_session_factory() as session:
            employee = Employee(name=data.name, tg_id=data.tg_id)
            session.add(employee)
            await session.commit()

        add_employee(data.name)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error creating new employee: {e}")
        return {"status": "error", "message": str(e)}


async def get_user_avatar_url(tg_user_id: int):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUserProfilePhotos"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"user_id": tg_user_id})

    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Telegram API error: {data.get('description')}")
    
    photos = data["result"]["photos"]
    if not photos:
        return None

    # gel small user circle avatar
    file_id = photos[0][0].get("file_id")
    if not file_id:
        return None
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_id}"

@app.get("/employees")
async def list_employees():
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Employee))
            employees = result.scalars().all()
            data = []
            for emp in employees:
                avatar_url = await get_user_avatar_url(emp.tg_id)
                tg_nickname = None
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, params={"chat_id": emp.tg_id})
                    chat_data = response.json()
                    if chat_data.get("ok"):
                        tg_nickname = chat_data["result"].get("username")
                except Exception as e:
                    print(f"Error fetching tg nickname for user {emp.tg_id}: {e}")
                data.append({
                    "id": emp.id,
                    "name": emp.name,
                    "tg_id": emp.tg_id,
                    "avatar_url": avatar_url,
                    "tg_nickname": tg_nickname
                })
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error listing employees: {e}")
        return {"status": "error", "message": str(e)}

class NewGroupAdmin(BaseModel):
    group_id: int
    tg_user_id: int

@app.post("/new_group_admin")
async def new_group_admin(data: NewGroupAdmin):
    try:
        async with async_session_factory() as session:
            group = await session.get(Group, data.group_id)
            if not group:
                return {"status": "error", "message": "Group not found"}

            admin = GroupAdmin(group_id=group.id, tg_user_id=data.tg_user_id)
            session.add(admin)
            await session.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error creating new group admin: {e}")
        return {"status": "error", "message": str(e)}

class EditEndWorkDayTime(BaseModel):
    time: str

@app.post("/edit_end_work_day_time")
async def edit_end_work_day_time(data: EditEndWorkDayTime):
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Setting).where(Setting.name == "end_work_day"))
            setting = result.scalar_one_or_none()
            if not setting:
                setting = Setting(name="end_work_day", value=data.time)
                session.add(setting)
            else:
                setting.value = data.time
            await session.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error editing end work day time: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/end_work_day_time")
async def get_end_work_day_time():
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Setting).where(Setting.name == "end_work_day"))
            setting = result.scalar_one_or_none()
            if not setting:
                return {"status": "error", "message": "Setting not found"}
            return {"status": "ok", "data": {"time": setting.value}}
    except Exception as e:
        print(f"Error fetching end work day time: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/group_admins/{group_id}")
async def list_group_admins(group_id: int):
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(GroupAdmin).where(GroupAdmin.group_id == group_id))
            admins = result.scalars().all()
            data = []
            for admin in admins:
                data.append({
                    "id": admin.id,
                    "tg_user_id": admin.tg_user_id
                })
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error listing group admins: {e}")
        return {"status": "error", "message": str(e)}


# check is user is admin of any group
@app.get("/is_user_group_admin/{tg_user_id}")
async def is_user_group_admin(tg_user_id: int):
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(GroupAdmin).where(GroupAdmin.tg_user_id == tg_user_id))
            admin = result.scalar_one_or_none()
            return {"status": "ok", "data": {"is_admin": admin is not None}}
    except Exception as e:
        print(f"Error checking if user is group admin: {e}")
        return {"status": "error", "message": str(e)}


# get last added shift where status is "need_check" and user is admin of group that shift belongs to (user can be admin of multiple groups)
@app.get("/last_shift_to_check/{tg_user_id}")
async def last_shift_to_check(tg_user_id: int):
    try:
        async with async_session_factory() as session:
            # get all groups where user is admin
            result = await session.execute(select(GroupAdmin).where(GroupAdmin.tg_user_id == tg_user_id))
            admin_groups = result.scalars().all()
            group_ids = [admin.group_id for admin in admin_groups]

            print(len(admin_groups))
            print(len(group_ids))
            if not group_ids:
                return {"status": "ok", "data": None}

            # get last shift with status "need_check" that belongs to one of these groups
            result = await session.execute(
                select(Shift)
                .where(Shift.status == "need_check")
                .where(Shift.group_id.in_(group_ids))
                .order_by(Shift.created_at.desc())
            )
            shift = result.scalar_one_or_none()
            
            if not shift:
                return {"status": "ok", "data": None}
            
            shift.status = "on_check"
            await session.commit()

            data = {
                "id": shift.id,
                "tg_chat_id": shift.tg_chat_id,
                "tg_message_id": shift.tg_message_id,
                "group_id": shift.group_id,
                "message_send_at": shift.message_send_at.isoformat(),
                "status": shift.status,
                "reason": shift.reason,
                "shift_date": shift.shift_date.isoformat(),
                "employee_id": shift.employee_id
            }
            return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error fetching last shift to check: {e}")
        return {"status": "error", "message": str(e)}


class IsShiftReady(BaseModel):
    shift_id: int
    is_ready: bool

@app.post("/set_shift_check_result")
async def set_shift_check_result(data: IsShiftReady):
    try:
        async with async_session_factory() as session:
            shift = await session.get(Shift, data.shift_id)
            if not shift:
                return {"status": "error", "message": "Shift not found"}

            if data.is_ready:
                shift.status = "ready"
                shift.reason = "admin"

                set_shift(shift.employee.name, shift.shift_date.day, shift.shift_date.month, 1)
            else:
                # delete shift
                await session.delete(shift)
            await session.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error setting shift check result: {e}")
        return {"status": "error", "message": str(e)}
