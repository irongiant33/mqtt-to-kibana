import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
import json
import ssl
import re
import data_processor

mqtt_broker_address = "0.0.0.0"
whisper_topic = "SDR/dev3/whisper"
message_processing = {
    "whisper_msg": [
        data_processor.remove_strings_within_square_brackets,
        data_processor.split_words_on_whitespace
        ]
}

es_host = "localhost"
es_port = 9200
es_index = "mqtt_data"
ca_cert_path = "/home/dev3/Downloads/http_ca.crt"
es_ssl_context = {"ca_certs": ca_cert_path, "minimum_version": ssl.PROTOCOL_TLSv1_2}

def on_connect(client, userdata, flags, rc):
    print("connected with result code " + str(rc))
    client.subscribe(whisper_topic)

def read_from_auth_file(auth_filename):
    with open(auth_filename) as fileobj:
        username, password = fileobj.readline().rstrip().split(":")
    return username, password

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode('utf-8'))
    except json.JSONDecodeError:
        return

    if not isinstance(payload, (dict, list)):
        return
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

    for key in message_processing:
        if key in payload:
            for function in message_processing[key]:
                payload[key] =function(payload[key])

    print(f'Received Payload:\n{json.dumps(payload, indent=4)}\n')
    es.index(index=es_index, body=payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_address, 1883, 60)
client.loop_forever()
