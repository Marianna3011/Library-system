from backend import utils
import uuid
from datetime import datetime, timedelta
import random

ROOMS = [1, 2, 3, 4, 5]
USERS = list(range(1001, 1201))  # 200 unique users
HOURS = list(range(8, 16))       # 8:00 to 15:00
DAYS = 30

today = datetime.today()

count = 0
for room in ROOMS:
    for day_offset in range(DAYS):
        date_str = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        user_id = random.choice(USERS)
        max_length = len(HOURS)
        length = random.randint(1, max_length)
        start_hour = random.choice(HOURS[:-(length-1) or None])  # Ensure it fits in the day
        for h in range(start_hour, start_hour + length):
            res_id = uuid.uuid4()
            success = utils.insert_reservation(room, date_str, h, user_id, res_id)
            if success:
                count += 1
