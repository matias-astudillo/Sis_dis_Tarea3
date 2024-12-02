import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, from_json, expr, decode, explode, lower, count, avg
from datetime import datetime

packages = [
    'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0',
    'com.datastax.spark:spark-cassandra-connector_2.12:3.4.0',
    'org.elasticsearch:elasticsearch-spark-30_2.12:8.16.0'
]

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("tarea3App") \
    .config("spark.jars.packages", ",".join(packages))\
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.es.nodes", "elasticsearch") \
    .config("spark.es.port", "9200") \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()

time.sleep(50)

# Leer datos desde Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "alerts_topic") \
    .load()

df = df.selectExpr("CAST(value AS STRING) as json_value")

# Deserializar el JSON
df = df.select(from_json(col("json_value"), "array<struct<city:string,type:string,street:string>>").alias("data"))
df = df.select(explode(col("data")).alias("data")).select("data.*")
df = df.withColumn("timestamp", current_timestamp())
df = df.withColumn("uuid", expr("uuid()"))
df = df.withColumn("type", lower(df["type"]))

# Función para escribir en Cassandra y elasticsearch según el tipo de alerta
def write_to_cassandra(df, epoch_id):
    print("Datos recibidos:")
    df.show(truncate=False)

    alert_types = df.select("type").distinct().rdd.flatMap(lambda x: x).collect()
    timeMetric = datetime.now()
    # Escribir en Cassandra para cada tipo de alerta
    for alert_type in alert_types:
        df_filtered = df.filter(col("type") == alert_type)
        df_filtered = df_filtered.drop("type")
        # Escribir los datos filtrados en Cassandra
        df_filtered.write \
            .format("org.apache.spark.sql.cassandra") \
            .option("keyspace", "alerts_keyspace") \
            .option("table", f"alerts_{alert_type}") \
            .option("checkpointLocation", f"/tmp/checkpoints/{alert_type}") \
            .mode("append") \
            .save()

        # Calcular la cantidad de alertas por tipo de alerta
        alert_count = df_filtered.count()

        # Calcular el promedio de alertas por cidudad por tipo de alerta
        avg_alerts_per_city = (
            df_filtered.groupBy("city")
            .agg(count("*").alias("city_alert_count"))
            .agg(avg("city_alert_count").alias("avg_city_alerts"))
            .collect()[0]["avg_city_alerts"]
        )

        # Crear un DataFrame para las métricas
        metrics_df = spark.createDataFrame(
            [
                {
                    "alert_type": alert_type,
                    "alert_count": alert_count,
                    "avg_alerts_per_city": avg_alerts_per_city,
                    "timestamp": timeMetric,
                }
            ]
        )
        # Escribir los métricas en elasticsearch
        metrics_df.write \
            .format("org.elasticsearch.spark.sql") \
            .option("es.resource", f"metrics") \
            .mode("append") \
            .save()
   

# Iniciar el stream utilizando foreachBatch para procesar los datos
query = df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_cassandra) \
    .start()

query.awaitTermination()