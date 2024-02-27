import socket
from .podtp_packet import PodtpPacket, PodtpType
from .link import WifiLink, LINK_MAX_WAIT_TIME

class Podtp:
    def __init__(self, server_ip, server_port):
        self.link = WifiLink(server_ip, server_port)

    def connect(self):
        self.link.connect()

    def disconnect(self):
        self.link.disconnect()

    def send(self, packet: PodtpPacket):
        self.link.send(packet)
    
    def send_reliable(self, packet: PodtpPacket, timeout = 1000) -> bool:
        for _ in range(timeout // LINK_MAX_WAIT_TIME):
            self.link.send(packet)
            ack = self.link.receive()
            if ack is None:
                continue
            elif ack.content.packet.header.type == PodtpType.PODTP_TYPE_ACK.value:
                return True
        return False