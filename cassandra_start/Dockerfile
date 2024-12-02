FROM python:3.9-slim

WORKDIR /app

RUN pip install cassandra-driver

COPY cassandra_start.py .

CMD ["python", "cassandra_start.py"]