from cassandra.cluster import Cluster
from backend.db import session
from cassandra.cluster import BatchStatement, SimpleStatement
from cassandra.util import uuid_from_time
from time import time

def get_reservations(room_id, date):
    try:
        query = "SELECT hour, user_id FROM reservations WHERE room_id=%s AND date=%s"
        rows = session.execute(query, (room_id, date))
        return sorted(rows, key=lambda r: r.hour)
    except Exception as e:
        print(f"Error getting reservations: {e}")
        return False

def check_next(room_id, date, hour, user_id):
    try:
        reservations = 1
        hour += 1
        query = "SELECT user_id FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
        result = session.execute(query, (room_id, date, hour)).one()
        us = result.user_id if result else None
        while us == user_id:
            reservations += 1
            hour += 1
            query = "SELECT * FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
            result = session.execute(query, (room_id, date, hour)).one()
            us = result.user_id if result else None

        return reservations
    except Exception as e:
        print(f"Error checking next reservation: {e}")
        return False

def update_reservation(room_id, date, old_hour, new_hour):
    try:
        query = "SELECT * FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
        result = session.execute(query, (room_id, date, old_hour)).one()
        if not result:
            return "No reservation found."
        delete_query = "DELETE FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
        session.execute(delete_query, (room_id, date, old_hour))
        insert_query = """INSERT INTO reservations (room_id, date, hour, user_id, res_id) VALUES (%s, %s, %s, %s, %s)"""
        session.execute(insert_query, (room_id, date, new_hour, result.user_id, result.res_id))
        return "Reservation updated."
    except Exception as e:
        print(f"Error updating reservation: {e}")
        return False

def delete_reservation(room_id, date, hour):
    try:
        query = "DELETE FROM reservations WHERE room_id=%s AND date=%s AND hour=%s"
        session.execute(query, (room_id, date, hour))
    except Exception as e:
        print(f"Error deleting reservation: {e}")
        return False

def insert_reservation(room_id, date, hour, user_id, res_id):
    try:
        query = "INSERT INTO reservations (room_id, date, hour, user_id, res_id) VALUES (%s, %s, %s, %s, %s)"
        session.execute(query, (room_id, date, hour, user_id, res_id))
    except Exception as e:
        print(f"Error creating reservation: {e}")
        return False
def make_reservation(room_id, date, hour, user_id):
    try: 
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
    except Exception as e:
        print(f"Error making reservation: {e}")
        return False

def cancel_reservations(reservation):
    try:
        session.execute("DELETE FROM reservations where room_id = %s and date = %s and hour = %s", (int(reservation[0]), reservation[1], int(reservation[2])))
    except Exception as e:
        print(f"Error canceling reservation: {e}")
        return False