FROM python:3.9-slim

WORKDIR /app

RUN pip install flask cassandra-driver

COPY monitoreo.py /app/monitoreo.py

CMD ["python", "monitoreo.py"]