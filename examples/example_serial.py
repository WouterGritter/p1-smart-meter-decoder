from smart_meter import SmartMeter

meter = SmartMeter('COM3', 115200)

while True:
    reading = meter.read_p1_packet()

    power_usage = reading['current_readings']['total']['power_delivery'] \
                  - reading['current_readings']['total']['power_redelivery']
    print(f'Current power usage: {power_usage} kW')
