from p1_decode import p1_decode
import pprint


f = open('dummy_reading.txt', 'r')
dummyReading = f.read()

decoded_reading = p1_decode(dummyReading)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(decoded_reading)
