from flask import json

from confluent_kafka import Producer

Producer = Producer({'bootstrap.servers': 'kafka:29092'})

def sendData(data, topic):
    datajson = json.dumps(data).encode('utf-8')
    Producer.produce(topic=topic, value=datajson)