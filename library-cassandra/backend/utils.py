from cassandra.cluster import Cluster
from backend.db import session
from cassandra.cluster import BatchStatement, SimpleStatement
from cassandra.util import uuid_from_time
from time import time

def get_reservations(room_id, date):
    query = "SELECT hour, user_id FROM reservations WHERE room_id=%s AND date=%s"
    rows = session.execute(query, (room_id, date))
    return sorted(rows, key=lambda r: r.hour)

def update_reservation(room_id, date, old_hour, new_hour):
    query = "SELECT * FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
    result = session.execute(query, (room_id, date, old_hour)).one()
    if not result:
        return "No reservation found."
    delete_query = "DELETE FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
    session.execute(delete_query, (room_id, date, old_hour))
    insert_query = """INSERT INTO reservations (room_id, date, hour, user_id, res_id) VALUES (%s, %s, %s, %s, %s)"""
    session.execute(insert_query, (room_id, date, new_hour, result.user_id, result.res_id))
    return "Reservation updated."

def delete_reservation(room_id, date, hour):
    query = "DELETE FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
    session.execute(query, (room_id, date, hour))

def insert_reservation(room_id, date, hour, user_id, res_id):
    query = "INSERT INTO reservations (room_id, date, hour, user_id, res_id) VALUES (%s, %s, %s, %s, %s)"
    session.execute(query, (room_id, date, hour, user_id, res_id))

def make_reservation(room_id, date, hour, user_id):
    query = session.prepare("""
        SELECT room_id, date, hour 
        FROM reservations 
        WHERE room_id = ? AND date = ? AND hour = ?
        """)
    rows = session.execute(query, (room_id, date, hour))
    if rows.one():
        print("The room is already reserved!")
    else:
        batch = BatchStatement()
        batch.add(SimpleStatement("INSERT INTO reservations (room_id, date, hour, user_id, res_id) values (%s, %s, %s, %s, %s)"), (room_id, date, hour, user_id, uuid_from_time(time())))
        session.execute(batch)

def cancel_reservations(reservation):
    session.execute("DELETE FROM reservations where room_id = %s and date = %s and hour = %s", (int(reservation[0]), reservation[1], int(reservation[2])))