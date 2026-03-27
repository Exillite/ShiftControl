import os
import gspread
from google.oauth2.service_account import Credentials
import redis
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON"), scopes=SCOPES)
client = gspread.authorize(creds)

redis_client = redis.from_url(os.getenv("CELERY_RESULT_BACKEND"))


def get_last_table_state():
    state = redis_client.get('last_table_state')
    if state:
        return json.loads(state)
    return None


def set_last_table_state(state):
    redis_client.set('last_table_state', json.dumps(state))


def add_employee(name):
    spreadsheet = client.open(os.getenv("GOOGLE_SHEET_NAME"))
    for i in range(13):
        sheet = spreadsheet.get_worksheet(i)

        names = sheet.col_values(1)
        for i in range(2, len(names)):
            if names[i] == "":
                row = i + 1
                break
        else:
            row = len(names) + 1

        sheet.update_cell(row, 1, name)
        
        sheet.update(f"B{row}:AF{row}", [[0]*31])


def set_shift(name, day, month, value):
    spreadsheet = client.open(os.getenv("GOOGLE_SHEET_NAME"))

    sheet = spreadsheet.get_worksheet(month - 1)

    names = sheet.col_values(1)

    try:
        row = names.index(name) + 1
    except ValueError:
        raise Exception("No employee with this name")

    col = day + 1

    sheet.update_cell(row, col, value)

def get_table_state():
    spreadsheet = client.open(os.getenv("GOOGLE_SHEET_NAME"))

    l = []
    for i in range(13):
        sheet = spreadsheet.get_worksheet(i)
        l.append(sheet.get("B3:AF1000"))
    return l


async def find_changes(olds, news, names):
    changes = []
    for m in range(13):
        old = olds[m]
        new = news[m]
        for i in range(len(new)):
            for j in range(len(new[i])):
                if old[i][j] != new[i][j]:
                    changes.append({
                        "employee": names[i],
                        "day": j + 1,
                        "set": new[i][j]
                    })
    return changes
