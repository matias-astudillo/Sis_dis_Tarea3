from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import time

app = Flask(__name__)

time.sleep(100)

# Conexión a Cassandra
cluster = Cluster(['cassandra'], port=9042)
session = cluster.connect()
session.set_keyspace('alerts_keyspace')

# Lista de tipos de alertas válidos
VALID_ALERT_TYPES = ['jam', 'chit_chat', 'road_closed', 'police', 'hazard', 'accident']

@app.route('/alert/<alert_type>', methods=['GET'])
def get_alert(alert_type):
    alert_type = alert_type.lower()
    if alert_type not in VALID_ALERT_TYPES:
        return jsonify({"error": f"El tipo de alerta '{alert_type}' no existe."}), 404

    # Nombre de la tabla
    table_name = f"alerts_{alert_type}"

    try:
        # Obtener el timestamp más reciente
        latest_timestamp_query = f"SELECT MAX(timestamp) AS latest_timestamp FROM {table_name}"
        latest_timestamp_result = session.execute(SimpleStatement(latest_timestamp_query)).one()
        latest_timestamp = latest_timestamp_result.latest_timestamp

        if not latest_timestamp:
            return jsonify({"message": "No se encontraron alertas recientes."}), 200

        # Obtener los registros con el timestamp más reciente
        data_query = f"SELECT city, street FROM {table_name} WHERE timestamp = %s ALLOW FILTERING;"
        rows = session.execute(SimpleStatement(data_query), (latest_timestamp,))

        # Formatear los resultados
        results = [{"city": row.city, "street": row.street} for row in rows]
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": "Error al consultar Cassandra.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)