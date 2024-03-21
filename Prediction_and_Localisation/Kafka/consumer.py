# consu9mer.py
def new():
    while True:

        from kafka import KafkaConsumer
        import json
        consumer = KafkaConsumer(
            'camera_700005261101',
            bootstrap_servers=['localhost:1093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        # note that this for loop will block forever to wait for the next message
        if consumer:
            print("co",consumer)
            for message in consumer:
                # pass
                print(message.value)
        else:
            print("waiting")        

if __name__=='__main__':
    new()
