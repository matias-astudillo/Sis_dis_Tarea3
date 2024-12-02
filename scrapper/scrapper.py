from kafka import KafkaConsumer, KafkaProducer
import time
import random
import requests
import json

def run():
    producer = KafkaProducer(bootstrap_servers='kafka:9092', api_version=(0, 10, 2))

    url = 'https://www.waze.com/live-map/api/georss?top=-33.25979857377675&bottom=-33.72157830761839&left=-71.0564118186012&right=-70.17805488500746&env=row&types=alerts,traffic'

    time.sleep(60)
    while True:
        response = requests.get(url)
        data = response.json()
        filtered_alerts = []
        for alert in data['alerts']:
            filtered_alert = {
                "city": alert.get("city"),
                "type": alert.get("type"),
                "street": alert.get("street")
            }
            filtered_alerts.append(filtered_alert)
        alertas = json.dumps(filtered_alerts).encode('utf-8')
        producer.send('alerts_topic', value=alertas)
        time.sleep(120)


if __name__ == '__main__':
    run()