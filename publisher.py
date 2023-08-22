import paho.mqtt.client as mqtt
import random
import time

# MQTT settings
mqtt_broker_address = "0.0.0.0"
mqtt_topic = "random_data_topic"
geo_topic = "geo_topic"

# create a client instance
client = mqtt.Client()

# connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic)

# publish random data
def publish_random_data():
    with open("sample_geo_data.json") as fileobj:
        geodata = fileobj.read()
    while True:
        random_value = random.randint(0, 100)
        client.publish(mqtt_topic, str(random_value))
        client.publish(geo_topic, geodata)
        print(f"Published {random_value} to {mqtt_topic}")
        time.sleep(2)

client.on_connect = on_connect
client.connect(mqtt_broker_address, 1883, 60)
client.loop_start()
publish_random_data()
