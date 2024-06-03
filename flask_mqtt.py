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
    delivery = reading['delivery/low_tariff'] + reading['delivery/high_tariff']
    redelivery = reading['redelivery/low_tariff'] + reading['redelivery/high_tariff']

    mqttc.publish(mqtt_topic('energy/delivery'), delivery, retain=True)
    mqttc.publish(mqtt_topic('energy/redelivery'), redelivery, retain=True)
    mqttc.publish(mqtt_topic('energy/total'), delivery - redelivery, retain=True)

    current = reading['current_readings']

    power_l1 = (current['L1']['power_delivery'] - current['L1']['power_delivery']) * 1000
    power_l2 = (current['L2']['power_delivery'] - current['L2']['power_delivery']) * 1000
    power_l3 = (current['L3']['power_delivery'] - current['L3']['power_delivery']) * 1000
    power_total = (current['total']['power_delivery'] - current['total']['power_delivery']) * 1000

    voltage_l1 = current['L1']['voltage']
    voltage_l2 = current['L2']['voltage']
    voltage_l3 = current['L3']['voltage']
    voltage_average = (voltage_l1 + voltage_l2 + voltage_l3) / 3

    amperage_l1 = power_l1 / voltage_l1
    amperage_l2 = power_l2 / voltage_l2
    amperage_l3 = power_l3 / voltage_l3
    amperage_total = amperage_l1 + amperage_l2 + amperage_l3

    mqttc.publish(mqtt_topic('power/l1'), power_l1, retain=True)
    mqttc.publish(mqtt_topic('power/l2'), power_l2, retain=True)
    mqttc.publish(mqtt_topic('power/l3'), power_l3, retain=True)
    mqttc.publish(mqtt_topic('power/total'), power_total, retain=True)

    mqttc.publish(mqtt_topic('voltage/l1'), voltage_l1, retain=True)
    mqttc.publish(mqtt_topic('voltage/l1'), voltage_l2, retain=True)
    mqttc.publish(mqtt_topic('voltage/l1'), voltage_l3, retain=True)
    mqttc.publish(mqtt_topic('voltage/average'), voltage_average, retain=True)

    mqttc.publish(mqtt_topic('amperage/l1'), amperage_l1, retain=True)
    mqttc.publish(mqtt_topic('amperage/l2'), amperage_l2, retain=True)
    mqttc.publish(mqtt_topic('amperage/l3'), amperage_l3, retain=True)
    mqttc.publish(mqtt_topic('amperage/total'), amperage_total, retain=True)


def mqtt_topic(attribute):
    return MQTT_TOPIC_FORMAT.replace('{attribute}', attribute)


thread = threading.Thread(target=serial_thread)
thread.start()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def flask_root():
    return jsonify(last_reading)


app.run(host="0.0.0.0", port=8080, debug=False)
