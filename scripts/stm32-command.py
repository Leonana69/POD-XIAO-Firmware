import json
from podtp import Podtp, PodtpPacket, PodtpType, PodtpPort
from podtp import print_t

def send_packet(podtp):
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_COMMAND,
                                      PodtpPort.PORT_)
    pass

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        send_packet(podtp)
        podtp.disconnect()

if __name__ == '__main__':
    main()