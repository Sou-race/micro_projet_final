from kafka import KafkaProducer


produceur = KafkaProducer(bootstrap_servers="kafka:9094")

def sendData(topic, data):
    produceur.send(topic, value=data)
