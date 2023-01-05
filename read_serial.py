import os

from dotenv import load_dotenv

from smart_meter import SmartMeter

load_dotenv()

SERIAL_PORT = os.getenv('SERIAL_PORT')
SERIAL_SPEED = int(os.getenv('SERIAL_SPEED'))

print(f'{SERIAL_PORT=}')
print(f'{SERIAL_SPEED=}')

meter = SmartMeter(SERIAL_PORT, SERIAL_SPEED)

while True:
    reading = meter.read_p1_packet()

    power_usage = reading['current_readings']['total']['power_delivery'] \
                  - reading['current_readings']['total']['power_redelivery']
    print(f'Current power usage: {power_usage} kW')
