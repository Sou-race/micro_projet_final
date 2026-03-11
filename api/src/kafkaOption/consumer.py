from kafka import KafkaConsumer

consumerData = KafkaConsumer("pytorchData","tensorflowData", auto_offset_reset='latest')
consumerLog = KafkaConsumer("logs", auto_offset_reset='latest')

def getModelData():
    for data in consumerData:
        print(data.value)
        print(data.offset)
    