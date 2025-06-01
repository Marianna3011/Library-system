from cassandra.cluster import Cluster

cluster = Cluster(['localhost'])  
session = cluster.connect('library')  