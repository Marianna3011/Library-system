from cassandra.cluster import Cluster
from cassandra.cluster import BatchStatement, SimpleStatement
from cassandra.util import uuid_from_time
from time import time
# connecting to the cluster
cluster = Cluster(['127.0.0.1'], port = 9042)
session = cluster.connect()

# create keyspace
keyspace = "create keyspace if not exists Library with replication={'class':'SimpleStrategy', 'replication_factor':1};"
session.execute(keyspace)
session.execute("use library;")
# create table
table = "create table if not exists reservations (room_id int, date date, hour int, user_id int, res_id uuid, primary key((room_id, date), hour));"
session.execute(table)


def operations():
    '''
        Operation is an integer:
        1. Make the reservation
        2. Update the reservation 
        3. See the reservation
        4. Cancel the reservation
        5. Exit the program
    '''
    print('Please enter which operation you would like to perform:\n 1. Make a reservation\n 2. Update a reservation\n 3. See the reservation\n 4. Cancel the reservation\n 5. Exit')
    operation = int(input())
    if operation == 1:
        print('Enter data for the reservation:\n')
        room_id = int(input('Room number: '))
        date = input('Date of the reservation: ')
        hour = int(input('Hour of the reservation: '))
        user_id = int(input('User number: '))
        make_reservation(room_id, date, hour, user_id)
        return 0
    elif operation == 4:
        print('Enter data of operations to be removed (enter done to stop): ')
        toBeRemoved = []
        e = ""
        while e != 'done':
            room_id = int(input('Room number: '))
            date = input('Date of the reservation: ')
            hour = int(input('Hour of the reservation: '))
            toBeRemoved.append([room_id, date, hour])
            e = input("Are you done")
        cancel_reservations(toBeRemoved)
        return 0
    else:
        return 1

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


def cancel_reservations(toBeRemoved):
    for reservation in toBeRemoved:
        session.execute("DELETE FROM reservations where room_id = %s and date = %s and hour = %s", (int(reservation[0]), reservation[1], int(reservation[2])))
op = operations()
while op != 1:
    op = operations()
cluster.shutdown()