from .podtp_packet import PodtpPacket, PodtpType
from .link import WifiLink, LINK_MAX_WAIT_TIME

class Podtp:
    def __init__(self, server_ip, server_port):
        self.link = WifiLink(server_ip, server_port)

    def connect(self) -> bool:
        return self.link.connect()

    def disconnect(self):
        self.link.disconnect()

    def send(self, packet: PodtpPacket) -> bool:
        if packet.content.packet.header.type == PodtpType.PODTP_TYPE_BOOT_LOADER.value:
            return self.send_reliable(packet)
        else:
            return self.link.send(packet)

    def send_once(self, packet: PodtpPacket) -> bool:
        self.link.send(packet)
        return True
    
    def send_reliable(self, packet: PodtpPacket) -> bool:
        self.link.send(packet)
        ack = self.link.receive()
        if ack and ack.content.packet.header.type == PodtpType.PODTP_TYPE_ACK.value:
            return True
        else:
            return False