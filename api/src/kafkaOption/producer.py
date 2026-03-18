from flask import json

from confluent_kafka import Producer

Producer = Producer({'bootstrap.servers': 'kafka:29092'})

test = {
    "testid": "1",
    "teststr": "test"
}

def sendData(data):
    datajson = json.dumps(data).encode('utf-8')
    Producer.produce(topic="test", value=datajson)