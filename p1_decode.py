import datetime


def p1_decode(reading):
    lines = reading.split('\n')[:-1]

    return {
        'header': lines[0],
        'footer': lines[-1],
        'version': decode_version(find_line(lines, '0.2.8')),
        'timestamp': decode_timestamp(get_raw_data(find_line(lines, '1.0.0'))[0]),
        'equipment_identifier': decode_equipment_identifier(find_line(lines, '96.1.1')),
        'current_tariff': decode_tariff(find_line(lines, '96.14.0')),
        'text_message': get_raw_data(find_line(lines, '96.13.0'))[0],
        'power_failures': {
            'total': int(get_raw_data(find_line(lines, '96.7.21'))[0]),
            'total_long': int(get_raw_data(find_line(lines, '96.7.9'))[0]),
            'event_log': decode_power_failures(find_line(lines, '99.97.0')),
        },
        'voltage_sags': {
            'L1': int(get_raw_data(find_line(lines, '32.32.0'))[0]),
            'L2': int(get_raw_data(find_line(lines, '52.32.0'))[0]),
            'L3': int(get_raw_data(find_line(lines, '72.32.0'))[0]),
        },
        'voltage_swells': {
            'L1': int(get_raw_data(find_line(lines, '32.36.0'))[0]),
            'L2': int(get_raw_data(find_line(lines, '52.36.0'))[0]),
            'L3': int(get_raw_data(find_line(lines, '72.36.0'))[0]),
        },
        'delivery': {
            'low_tariff': decode_unit(get_raw_data(find_line(lines, '1.8.1'))[0]),   # kWh
            'high_tariff': decode_unit(get_raw_data(find_line(lines, '1.8.2'))[0]),  # kWh
        },
        'redelivery': {
            'low_tariff': decode_unit(get_raw_data(find_line(lines, '2.8.1'))[0]),   # kWh
            'high_tariff': decode_unit(get_raw_data(find_line(lines, '2.8.2'))[0]),  # kWh
        },
        'current_readings': {
            'L1': {
                'voltage': decode_unit(get_raw_data(find_line(lines, '32.7.0'))[0]),           # V
                'amperage': decode_unit(get_raw_data(find_line(lines, '31.7.0'))[0]),          # A
                'power_delivery': decode_unit(get_raw_data(find_line(lines, '21.7.0'))[0]),    # kW
                'power_redelivery': decode_unit(get_raw_data(find_line(lines, '22.7.0'))[0]),  # kW
            },
            'L2': {
                'voltage': decode_unit(get_raw_data(find_line(lines, '52.7.0'))[0]),           # V
                'amperage': decode_unit(get_raw_data(find_line(lines, '51.7.0'))[0]),          # A
                'power_delivery': decode_unit(get_raw_data(find_line(lines, '41.7.0'))[0]),    # kW
                'power_redelivery': decode_unit(get_raw_data(find_line(lines, '42.7.0'))[0]),  # kW
            },
            'L3': {
                'voltage': decode_unit(get_raw_data(find_line(lines, '72.7.0'))[0]),           # V
                'amperage': decode_unit(get_raw_data(find_line(lines, '71.7.0'))[0]),          # A
                'power_delivery': decode_unit(get_raw_data(find_line(lines, '61.7.0'))[0]),    # kW
                'power_redelivery': decode_unit(get_raw_data(find_line(lines, '62.7.0'))[0]),  # kW
            },
            'total': {
                'power_delivery': decode_unit(get_raw_data(find_line(lines, '1.7.0'))[0]),     # kW
                'power_redelivery': decode_unit(get_raw_data(find_line(lines, '2.7.0'))[0]),   # kW
            },
        },
    }


def find_line(lines, looking_for):
    for line in lines:
        if looking_for in line:
            return line

    return None


def get_raw_data(line):
    data = line.split('(')[1:]
    data = [d[0:-1] for d in data]

    return data


def decode_version(line):
    version = get_raw_data(line)[0]
    return version[0:-1] + '.' + version[-1]


def decode_timestamp(data):
    decoded_date = datetime.datetime(
        int(data[0:2]) + 2000,  # year
        int(data[2:4]),         # month
        int(data[4:6]),         # day
        int(data[6:8]),         # hour
        int(data[8:10]),        # minute
        int(data[10:12]),       # second
    )

    return str(decoded_date)


def decode_equipment_identifier(line):
    return get_raw_data(line)[0]


def decode_unit(data):
    return float(data.split('*', 2)[0])


def decode_tariff(line):
    return 'high' if int(get_raw_data(line)[0]) == 2 else 'low'


def decode_power_failures(line):
    power_failures = []

    power_failure_data = get_raw_data(line)[2:]
    for i in range(0, len(power_failure_data), 2):
        timestamp = decode_timestamp(power_failure_data[i])
        length = decode_unit(power_failure_data[i + 1])

        power_failures.append({
            'timestamp': timestamp,
            'length': length,
        })

    return power_failures
