from celery import shared_task
from core.gsheets.sheets_edit import get_table_state, find_changes, get_last_table_state, set_last_table_state
from core.db.models import Shift, Employee
from sqlalchemy import select
from core.db.database import async_session_factory
import asyncio


async def _make_update():
    old_state = get_last_table_state()
    new_state = get_table_state()
    names = [row[0] for row in new_state[0]]
    changes = await find_changes(old_state, new_state, names)
    set_last_table_state(new_state)

    for c in changes:
        async with async_session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.name == c["employee"]))
            employee = result.scalar_one_or_none()
            if not employee:
                continue

            result = await session.execute(select(Shift).where(Shift.employee_id == employee.id, Shift.shift_date.day == c["day"], Shift.shift_date.month == c["month"]))
            shift = result.scalar_one_or_none()
            if not shift:
                continue

            if c["value"] == "0":
                # delete shift
                await session.delete(shift)
            else:
                shift.status = "ready"
                shift.reason = "sheet"

            await session.commit()
    



@shared_task
def check_sheet_updates():
    if get_last_table_state() is None:
        set_last_table_state(get_table_state())
        return
    asyncio.run(_make_update())
    
