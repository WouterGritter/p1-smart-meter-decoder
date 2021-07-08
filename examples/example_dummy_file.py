from p1_decode import p1_decode


def print_dict(dictionary, spaces=0):
    for key in dictionary:
        value = dictionary[key]
        if type(value) is dict:
            print(spaces*' ' + f'{key} =')
            print_dict(value, spaces + 2)
        else:
            print(spaces*' ' + f'{key} = {value}')


f = open('dummy_reading.txt', 'r')
dummyReading = f.read()

decoded_reading = p1_decode(dummyReading)

print_dict(decoded_reading)
