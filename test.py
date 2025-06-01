from cassandra.cluster import Cluster

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

def make_reservation(room_id, date, hour, user_id):
    query = session.prepare("""
        SELECT room_id, date, hour 
        FROM reservations 
        WHERE room_id = ? AND date = ? AND hour = ?
        """)
    rows = session.execute(query, (room_id, date, hour))
    if rows.one():
        print("You can't make this reservation!")

make_reservation(2, '2025-05-01', 15, 3)
cluster.shutdown()