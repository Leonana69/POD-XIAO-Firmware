from typing import Optional
from .podtp_packet import PodtpPacket, PodtpType, PodtpPort
from .link import WifiLink
from .utils import print_t

class Podtp:
    def __init__(self, config: dict):
        self.link = WifiLink(config["ip"], config["port"])

    def connect(self) -> bool:
        return self.link.connect()

    def disconnect(self):
        self.link.disconnect()

    def send(self, packet: PodtpPacket) -> bool:
        if packet.header.type == PodtpType.PODTP_TYPE_BOOT_LOADER:
            return self.send_reliable(packet)
        else:
            return self.send_once(packet)
        
    def receive(self) -> Optional[PodtpPacket]:
        return self.link.receive()

    def send_once(self, packet: PodtpPacket) -> bool:
        return self.link.send(packet)
    
    def send_reliable(self, packet: PodtpPacket) -> bool:
        self.link.send(packet)
        ack = self.link.receive()
        if ack and ack.header.type == PodtpType.PODTP_TYPE_ACK \
               and ack.header.port == PodtpPort.PORT_OK:
            return True
        else:
            return False
        
    def stm32_enable(self, disable = False):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32,
            PodtpPort.PORT_ENABLE_STM32 if not disable else PodtpPort.PORT_DISABLE_STM32)
        self.send(packet)

    def esp32_echo(self):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32, PodtpPort.PORT_ECHO)
        self.send(packet)
        packet = self.receive()
        if packet:
            print_t(packet)