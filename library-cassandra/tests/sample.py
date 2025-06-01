from cassandra.cluster import Cluster
import uuid
from datetime import date

cluster = Cluster(['localhost'])
session = cluster.connect('library') 

room_id = 1
user_id = 42
sample_date = date.today().isoformat()
hours = [8, 9, 10]

for hour in hours:
    res_id = uuid.uuid4()
    session.execute(
        """
        INSERT INTO reservations (room_id, date, hour, user_id, res_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (room_id, sample_date, hour, user_id, res_id)
    )

print(f"Sample grouped reservation for user {user_id} in room {room_id} inserted for hours {hours}.")