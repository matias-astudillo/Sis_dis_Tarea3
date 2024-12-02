FROM bitnami/spark:3.4.0

COPY apache_spark.py /opt/spark/app/apache_spark.py

# Configurar el punto de entrada
CMD ["/opt/bitnami/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.16.0", "/opt/spark/app/apache_spark.py"]