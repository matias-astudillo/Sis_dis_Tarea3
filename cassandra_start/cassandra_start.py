from cassandra.cluster import Cluster
import time

time.sleep(80)

cluster = Cluster(['cassandra'], port=9042)

session = cluster.connect()

# Crear el keyspace si no existe
create_keyspace = """
CREATE KEYSPACE IF NOT EXISTS alerts_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
"""
session.execute(create_keyspace)

# Lista de tipos de alerta
alert_types = ['JAM', 'CHIT_CHAT', 'ROAD_CLOSED', 'POLICE', 'HAZARD', 'ACCIDENT']

# Crear las tablas correspondientes para cada tipo de alerta
for alert_type in alert_types:
    create_table = f"""
    CREATE TABLE IF NOT EXISTS alerts_keyspace.alerts_{alert_type} (
        uuid UUID PRIMARY KEY,
        city TEXT,
        street TEXT,
        timestamp TIMESTAMP
    );
    """
    session.execute(create_table)