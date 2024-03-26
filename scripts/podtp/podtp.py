import queue
import struct
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
                if packet.header.type == PodtpType.PODTP_TYPE_LOG:
                    print_t(f'Log: {packet.data[:packet.length - 1].decode()}', end='')
                else:
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

    def send_ctrl_lock(self, lock: bool) -> bool:
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_CTRL,
                                          PodtpPort.PODTP_PORT_LOCK if lock else PodtpPort.PODTP_PORT_UNLOCK)
        return self.send_packet(packet, ack=True)

    def send_command_setpoint(self, roll: float, pitch: float, yaw: float, thrust: float):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_COMMAND, PodtpPort.PODTP_PORT_RPYT)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', roll, pitch, yaw, thrust)
        packet.length = 1 + size
        self.send_packet(packet)

    def send_command_hover(self, height: float, vx: float, vy: float, vyaw: float):
        packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_COMMAND, PodtpPort.PODTP_PORT_HOVER)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', height, vx, vy, vyaw)
        packet.length = 1 + size
        self.send_packet(packet)