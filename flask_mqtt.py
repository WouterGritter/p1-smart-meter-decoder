import os

from dotenv import load_dotenv

from smart_meter import SmartMeter
import threading
from flask import Flask, jsonify

import paho.mqtt.client as mqtt

load_dotenv()

SERIAL_PORT = os.getenv('SERIAL_PORT')
SERIAL_SPEED = int(os.getenv('SERIAL_SPEED'))

MQTT_BROKER_ADDRESS = os.getenv('MQTT_BROKER_ADDRESS')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
MQTT_TOPIC_FORMAT = os.getenv('MQTT_TOPIC_FORMAT', 'p1/{attribute}')

print(f'{SERIAL_PORT=}')
print(f'{SERIAL_SPEED=}')
print(f'{MQTT_BROKER_ADDRESS=}')
print(f'{MQTT_BROKER_PORT=}')
print(f'{MQTT_TOPIC_FORMAT=}')

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, 60)
mqttc.loop_start()

smart_meter = SmartMeter(SERIAL_PORT, SERIAL_SPEED)
last_reading = None


def serial_thread():
    global last_reading

    while True:
        reading = smart_meter.read_p1_packet()
        if reading is not None:
            last_reading = reading
            publish_mqtt(reading)


def publish_mqtt(reading):
    delivery = reading['delivery']['low_tariff'] + reading['delivery']['high_tariff']
    redelivery = reading['redelivery']['low_tariff'] + reading['redelivery']['high_tariff']

    mqtt_publish('energy/delivery', delivery)
    mqtt_publish('energy/redelivery', redelivery)
    mqtt_publish('energy/total', delivery - redelivery)

    current = reading['current_readings']

    power_l1 = (current['L1']['power_delivery'] - current['L1']['power_redelivery']) * 1000
    power_l2 = (current['L2']['power_delivery'] - current['L2']['power_redelivery']) * 1000
    power_l3 = (current['L3']['power_delivery'] - current['L3']['power_redelivery']) * 1000
    power_total = (current['total']['power_delivery'] - current['total']['power_redelivery']) * 1000

    voltage_l1 = current['L1']['voltage']
    voltage_l2 = current['L2']['voltage']
    voltage_l3 = current['L3']['voltage']
    voltage_average = (voltage_l1 + voltage_l2 + voltage_l3) / 3

    amperage_l1 = power_l1 / voltage_l1
    amperage_l2 = power_l2 / voltage_l2
    amperage_l3 = power_l3 / voltage_l3
    amperage_total = abs(amperage_l1) + abs(amperage_l2) + abs(amperage_l3)

    mqtt_publish('power/l1', power_l1)
    mqtt_publish('power/l2', power_l2)
    mqtt_publish('power/l3', power_l3)
    mqtt_publish('power/total', power_total)

    mqtt_publish('voltage/l1', voltage_l1)
    mqtt_publish('voltage/l2', voltage_l2)
    mqtt_publish('voltage/l3', voltage_l3)
    mqtt_publish('voltage/average', voltage_average)

    mqtt_publish('amperage/l1', amperage_l1)
    mqtt_publish('amperage/l2', amperage_l2)
    mqtt_publish('amperage/l3', amperage_l3)
    mqtt_publish('amperage/total', amperage_total)

    gas_usage = reading['gas_usage']
    mqtt_publish('gas', gas_usage)


def mqtt_publish(attribute, value):
    topic = MQTT_TOPIC_FORMAT.replace('{attribute}', attribute)
    mqttc.publish(topic, round(value, 2), qos=0, retain=True)


thread = threading.Thread(target=serial_thread)
thread.start()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def flask_root():
    return jsonify(last_reading)


app.run(host="0.0.0.0", port=8080, debug=False)
