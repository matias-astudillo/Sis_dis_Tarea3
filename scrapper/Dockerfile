FROM python:3.9
WORKDIR /app

RUN pip install kafka-python requests

COPY ./scrapper.py .

CMD ["python", "scrapper.py"]