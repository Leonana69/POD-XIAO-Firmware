import queue
import struct
import time
from typing import Optional
from threading import Thread
from .podtp_packet import PodtpPacket, PodtpType, PodtpPort
from .link import WifiLink
from .utils import print_t

COMMAND_TIMEOUT_MS = 450

class Podtp:
    def __init__(self, config: dict):
        self.link = WifiLink(config["ip"], config["port"])
        self.packet_queue = {}
        self.last_packet_time = time.time()
        for type in PodtpType:
            self.packet_queue[type.value] = queue.Queue()

    def connect(self) -> bool:
        self.connected = self.link.connect()
        if self.connected:
            self.packet_thread = Thread(target=self.receive_packets)
            self.packet_thread.start()
            self.keep_alive_thread = Thread(target=self.keep_alive)
            self.keep_alive_thread.start()
        return self.connected

    def disconnect(self):
        self.connected = False
        self.packet_thread.join()
        self.keep_alive_thread.join()
        self.link.disconnect()

    def keep_alive(self):
        while self.connected:
            if time.time() - self.last_packet_time > COMMAND_TIMEOUT_MS / 1000:
                self.last_packet_time = time.time()
                packet = PodtpPacket().set_header(PodtpType.CTRL, PodtpPort.KEEP_ALIVE)
                self.send_packet(packet)
            time.sleep(0.05)

    def receive_packets(self):
        while self.connected:
            packet = self.link.receive()
            if packet:
                if packet.header.type == PodtpType.LOG:
                    print_t(f'Log: {packet.data[:packet.length - 1].decode()}', end='')
                else:
                    self.packet_queue[packet.header.type].put(packet)
        
    def get_packet(self, type: PodtpType, timeout = 1) -> Optional[PodtpPacket]:
        try:
            return self.packet_queue[type.value].get(timeout = timeout)
        except queue.Empty:
            return None
    
    def send_packet(self, packet: PodtpPacket, timeout = 2) -> bool:
        self.last_packet_time = time.time()
        self.link.send(packet)
        if packet.header.ack:
            packet = self.get_packet(PodtpType.ACK, timeout)
            if not packet or packet.header.port != PodtpPort.OK:
                return False
        return True
        
    def stm32_enable(self, disable = False):
        packet = PodtpPacket().set_header(PodtpType.ESP32,
            PodtpPort.ENABLE_STM32 if not disable else PodtpPort.DISABLE_STM32)
        self.send_packet(packet)

    def esp32_echo(self):
        packet = PodtpPacket().set_header(PodtpType.ESP32, PodtpPort.ECHO)
        self.send_packet(packet)
        packet = self.get_packet(PodtpType.ESP32)

    def send_ctrl_lock(self, lock: bool) -> bool:
        packet = PodtpPacket().set_header(PodtpType.CTRL,
                                          PodtpPort.LOCK if lock else PodtpPort.UNLOCK,
                                          ack=True)
        return self.send_packet(packet)

    def send_command_setpoint(self, roll: float, pitch: float, yaw: float, thrust: float) -> bool:
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.RPYT, ack=True)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', roll, pitch, yaw, thrust)
        packet.length = 1 + size
        return self.send_packet(packet)

    def send_command_hover(self, height: float, vx: float, vy: float, vyaw: float) -> bool:
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.HOVER, ack=True)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', height, vx, vy, vyaw)
        packet.length = 1 + size
        return self.send_packet(packet)