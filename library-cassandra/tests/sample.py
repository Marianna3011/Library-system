from cassandra.cluster import Cluster
import uuid
from datetime import date
from backend import utils
import threading
import time
import random

rooms = [1, 2, 3, 4, 5]
user_id = [1, 2]
sample_date = date.today().isoformat()
hours = range(8, 15)


def test1():
    def rapid_request(user_id, room, date):
        passed = True
        for hour in range(8, 15):
            try:
                utils.make_reservation(room, date, hour, user_id)
            except Exception as e:
                print(f"Failed at hour {hour}: {e}")
                print("Test 1 failed :(")
                passed = False
        if passed:
            print('Test 1 passed :)')
            
    thread = threading.Thread(target=rapid_request, args=(1, 1, '2025-06-08'))
    thread.start()
    thread.join()
    
    
def test2():
    def random_client(user_id, date):
        passed = True
        for _ in range(10):
            room = random.choice(rooms)
            hour = random.randint(8, 15)
            try:
                utils.make_reservation(room, date, hour, user_id)
            except Exception as e:
                print(f"User {user_id} failed at room {room} hour {hour}: {e}")
                print('Test 2 failed :(')
                passed = False
        if passed:
            print('Test 2 passed :)')
            
    threads = []
    for uid in range(1, 6):
        t = threading.Thread(target=random_client, args = (uid, '2025-06-10'))
        threads.append(t)
        t.start()


def test3():
    def occupy_all(user_id, date):
        passed = True
        for room in range(1, 6):
            for hour in range(8, 15):
                try:
                    utils.make_reservation(room, date, hour, user_id)
                except Exception as e:
                    print(f"User {user_id} conflict: Room {room}, Hour {hour}: {e}")
                    print('Test 3 failed :(')
                    passed = False
        if passed:
            print('Test 3 passed :)')
    
    t1 = threading.Thread(target=occupy_all, args=(1, '2025-06-11'))
    t2 = threading.Thread(target=occupy_all, args=(2, '2025-06-11'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    

def test4():
    def reserve_cancel_loop(user_id, room, date):
        passed = True
        for hour in range(8, 15):
            try:    
                utils.make_reservation(room, date, hour, user_id)
                utils.cancel_reservations([room, date, hour])
            except Exception as e:
                print(f"Loop error: {e}")
                print('Test 4 failed :(')
                passed = False
        if passed:
            print('Test 4 passed :)')
    
    t1 = threading.Thread(target=reserve_cancel_loop, args=(1, 1, '2025-06-12'))
    t2 = threading.Thread(target=reserve_cancel_loop, args=(2, 1, '2025-06-12'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def test5():
    def bulk_cancel(user_id, room, date):
        passed = True
        try:
            for hour in range(8, 16):
                utils.make_reservation(room, date, hour, user_id)
            for hour in range(8, 16):
                utils.cancel_reservations([room, date, hour])
            print(f"User {user_id} group cancel done.")
        except Exception as e:
            print(f"Bulk cancel error: {e}")
            print('Test 5 failed :(')
            passed = False
        if passed:
            print('Test 5 passed :)')

    t1 = threading.Thread(target=bulk_cancel, args=(1, 2, '2025-06-13'))
    t2 = threading.Thread(target=bulk_cancel, args=(2, 2, '2025-06-13'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

test1()
test2()
test3()
test4()
test5()