import os

from dotenv import load_dotenv

from smart_meter import SmartMeter
import threading
from flask import Flask, jsonify

load_dotenv()

SERIAL_PORT = os.getenv('SERIAL_PORT')
SERIAL_SPEED = int(os.getenv('SERIAL_SPEED'))

print(f'{SERIAL_PORT=}')
print(f'{SERIAL_SPEED=}')

smart_meter = SmartMeter(SERIAL_PORT, SERIAL_SPEED)
last_reading = None


def serial_thread():
    global last_reading

    while True:
        reading = smart_meter.read_p1_packet()
        if reading is not None:
            last_reading = smart_meter.read_p1_packet()


thread = threading.Thread(target=serial_thread)
thread.start()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def flask_root():
    return jsonify(last_reading)


app.run(host="0.0.0.0", port=8080, debug=False)
