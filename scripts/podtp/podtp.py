import queue
from typing import Optional
from threading import Thread
from .podtp_packet import PodtpPacket, PodtpType, PodtpPort
from .link import WifiLink
from .utils import print_t

class Podtp:
    def __init__(self, config: dict):
        self.link = WifiLink(config["ip"], config["port"])
        self.packet_queue = {}
        for type in PodtpType:
            self.packet_queue[type.value] = queue.Queue()

    def connect(self) -> bool:
        self.connected = self.link.connect()
        if self.connected:
            self.packet_thread = Thread(target=self.receive_packets)
            self.packet_thread.start()
        return self.connected

    def disconnect(self):
        self.connected = False
        self.packet_thread.join()
        self.link.disconnect()

    def receive_packets(self):
        while self.connected:
            packet = self.link.receive()
            if packet:
                self.packet_queue[packet.header.type].put(packet)
        
    def get_packet(self, type: PodtpType, timeout = 1) -> Optional[PodtpPacket]:
        try:
            return self.packet_queue[type.value].get(timeout = timeout)
        except queue.Empty:
            return None
    
    def send_packet(self, packet: PodtpPacket, ack = False, timeout = 1) -> bool:
        self.link.send(packet)
        if ack:
            packet = self.get_packet(PodtpType.PODTP_TYPE_ACK, timeout)
            if not packet or packet.header.port != PodtpPort.PORT_OK:
                return False
        return True
        
    def stm32_enable(self, disable = False):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32,
            PodtpPort.PORT_ENABLE_STM32 if not disable else PodtpPort.PORT_DISABLE_STM32)
        self.send_packet(packet)

    def esp32_echo(self):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32, PodtpPort.PORT_ECHO)
        self.send_packet(packet)
        packet = self.get_packet(PodtpType.PODTP_TYPE_ESP32)