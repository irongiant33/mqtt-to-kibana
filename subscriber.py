import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
import ssl

mqtt_broker_address = "0.0.0.0"
mqtt_topic = "random_data_topic"
geo_topic = "geo_topic"

es_host = "localhost"
es_port = 9200
es_index = "mqtt_data"
ca_cert_path = "/home/dev3/Downloads/http_ca.crt"
es_ssl_context = {"ca_certs": ca_cert_path, "minimum_version": ssl.PROTOCOL_TLSv1_2}

def on_connect(client, userdata, flags, rc):
    print("connected with result code " + str(rc))
    client.subscribe(mqtt_topic)
    client.subscribe(geo_topic)

def read_from_auth_file(auth_filename):
    with open(auth_filename) as fileobj:
        username, password = fileobj.readline().rstrip().split(":")
    return username, password

def on_message(client, userdata, message):
    payload = message.payload.decode('utf-8')
    print("Received message: ", payload)

    username, password = read_from_auth_file(".passwords")
    # push data to elasticsearch
    es = Elasticsearch(
        hosts=[
                f"https://{es_host}:{es_port}"
        ],
        http_auth=(username, password),
        verify_certs=True,
        ca_certs=ca_cert_path,
    )
    data = {
            "message": payload,
            f"{message.topic}": message.topic,
            }
    es.index(index=es_index, body=data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_address, 1883, 60)
client.loop_forever()
