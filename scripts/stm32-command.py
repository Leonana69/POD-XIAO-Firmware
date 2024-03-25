import json, struct
from podtp import Podtp, PodtpPacket, PodtpType, PodtpPort
from podtp import print_t

def send_packet(podtp):
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_COMMAND,
                                      PodtpPort.PODTP_PORT_RPYT)
    roll = 0.0
    pitch = 0.0
    yaw = 0.0
    thrust = 10000.0

    size = struct.calcsize('<ffff')
    packet.data[:size] = struct.pack('<ffff', roll, pitch, yaw, thrust)
    packet.length = 1 + size
    podtp.send(packet)

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        send_packet(podtp)
        podtp.disconnect()

if __name__ == '__main__':
    main()