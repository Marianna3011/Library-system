from cassandra.cluster import Cluster

cluster = Cluster(['localhost'])  
session = cluster.connect()

# create keyspace
keyspace = "create keyspace if not exists Library with replication={'class':'SimpleStrategy', 'replication_factor':1};"
session.execute(keyspace)
session.execute("use library;")
# create table
table = "create table if not exists reservations (room_id int, date date, hour int, user_id int, res_id uuid, primary key((room_id, date), hour));"
session.execute(table)