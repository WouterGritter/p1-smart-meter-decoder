import serial
from p1_decode import p1_decode


class SmartMeter(serial.Serial):
    def read_p1_packet(self):
        try:
            packet = ''
            line = ''

            while '!' not in line:
                line = self.readline().decode()
                line = line.replace('\r', '')
                packet += line

            decoded_packet = p1_decode(packet)
            return decoded_packet
        except:
            return None
