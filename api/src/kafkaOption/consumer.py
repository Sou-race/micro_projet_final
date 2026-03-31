from confluent_kafka import Consumer
from flask import json

consumerConfig = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'dataModel',
    'auto.offset.reset':'latest',
    'session.timeout.ms': 6000,
    'heartbeat.interval.ms': 2000
}

consumerModel = Consumer(consumerConfig)
consumerModel.subscribe(['pytorch', 'tensorflow'])

def consumeData():
    result = consumerModel.poll(1.0)
    if result == None:
        return None
    if result.error():
        return None
    return result

def _make_consumer(topic):
    c = Consumer({
        'bootstrap.servers': 'kafka:29092',
        'group.id': f'dataModel-{topic}',
        'auto.offset.reset': 'latest',
        'session.timeout.ms': 6000,
        'heartbeat.interval.ms': 2000
    })
    c.subscribe([topic])
    return c