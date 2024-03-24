import argparse

from podtp import Podtp
from podtp.podtp_packet import PODTP_MAX_DATA_LEN

DEFAULT_SERVER_IP = '10.0.0.115'  # Replace with your ESP32's IP address
# DEFAULT_SERVER_IP = '192.168.0.131'  # Replace with your ESP32's IP address
DEFAULT_SERVER_PORT = 80  # Replace with your ESP32's port number

def main():
    parser = argparse.ArgumentParser(description='Upload firmware to STM32 via ESP32 over WiFi')
    parser.add_argument('-i', '--ip', help='IP address of the ESP32', type=str, default=DEFAULT_SERVER_IP, required=False)
    parser.add_argument('-p', '--port', help='Port number of the ESP32', type=int, default=DEFAULT_SERVER_PORT, required=False)
    args = parser.parse_args()
    
    podtp = Podtp(args.ip, args.port)
    if podtp.connect():
        podtp.esp32_echo()
        podtp.disconnect()

if __name__ == '__main__':
    main()