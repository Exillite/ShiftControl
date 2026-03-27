import httpx
import os

API_BASE = os.getenv("CORE_SERVER_URL")


class APIClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10)


    async def _get(self, path: str):
        try:
            response = await self.client.get(f"{API_BASE}{path}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ GET {path} error: {e}")
            return {"status": "error", "data": []}


    async def _post(self, path: str, json: dict):
        try:
            response = await self.client.post(f"{API_BASE}{path}", json=json)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ POST {path} error: {e}")
            return {"status": "error"}


    async def get_groups(self):
        return await self._get("/groups")

    async def create_group(self, tg_chat_id: int):
        return await self._post("/new_group", {"tg_chat_id": tg_chat_id})

    async def get_group(self, group_id: int):
        return await self._get(f"/group?group_id={group_id}")


    async def get_objects(self):
        return await self._get("/objects")

    async def create_object(self, name: str):
        return await self._post("/new_object", {"name": name})

    async def assign_object(self, group_id: int, object_id: int):
        return await self._post("/assign_group_to_object", {
            "group_id": group_id,
            "object_id": object_id
        })


    async def get_group_admins(self, group_id: int):
        return await self._get(f"/group_admins/{group_id}")
    
    async def create_group_admin(self, group_id: int, tg_user_id: int):
        return await self._post("/new_group_admin", {
            "group_id": group_id,
            "tg_user_id": tg_user_id
        })
    
    async def get_work_time(self):
        return await self._get("/end_work_day_time")

    async def set_work_time(self, time: str):
        return await self._post("/edit_end_work_day_time", {"time": time})

    async def is_user_admin(self, tg_user_id: int):
        return await self._get(f"/is_user_group_admin/{tg_user_id}")
    
    async def get_shift_for_check(self, tg_user_id: int):
        return await self._get(f"/last_shift_to_check/{tg_user_id}")

    async def set_shift_result(self, shift_id: int, is_ready: bool):
        return await self._post("/set_shift_check_result", {
            "shift_id": shift_id,
            "is_ready": is_ready
        })
    
    async def create_employee(self, name: str, tg_id: int):
        return await self._post("/new_employee", {
            "name": name,
            "tg_id": tg_id
        })


# singleton
api = APIClient()