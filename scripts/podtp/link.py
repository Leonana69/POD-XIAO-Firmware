import socket
import select
import queue
from enum import Enum
from typing import Optional

from .podtp_packet import *
from .utils import print_t

LINK_MAX_WAIT_TIME = 500

class WifiLinkState(Enum):
    PODTP_STATE_START_1 = 0
    PODTP_STATE_START_2 = 1
    PODTP_STATE_LENGTH = 2
    PODTP_STATE_RAW_DATA = 3

class WifiLink:
    def __init__(self, server_ip: str, server_port: int):
        self.link_state = WifiLinkState.PODTP_STATE_START_1
        self.length = 0
        self.packet = PodtpPacket()
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(LINK_MAX_WAIT_TIME / 1000)
        self.client_connected = False
        self.packet_queue = queue.Queue()

    def connect(self) -> bool:
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_connected = True
            print_t(f'Connected to {self.server_ip}:{self.server_port}')
            return True
        except:
            print_t(f'Failed to connect to {self.server_ip}:{self.server_port}')
            return False

    def disconnect(self):
        self.client_socket.close()
        self.client_connected = False
        print_t(f'Disconnected from {self.server_ip}:{self.server_port}')

    def send(self, packet: PodtpPacket) -> bool:
        if not self.client_connected:
            print_t(f'Failed to send packet: Not connected to {self.server_ip}:{self.server_port}')
            return False
        self.client_socket.send(packet.pack())
        return True

    def receive(self, timeout = 0.1) -> Optional[PodtpPacket]:
        """
        Read from the TCP connection until a packet is returned, or a timeout occurs.
        :param timeout: The number of seconds to wait for a complete packet.
        :return: A PodtpPacket if one is successfully received, None otherwise.
        """
        if not self.client_connected:
            print_t(f'Failed to receive packet: Not connected to {self.server_ip}:{self.server_port}')
            return None
        while True:
            readable, _, _ = select.select([self.client_socket], [], [], timeout)
            if not readable:
                return None

            data = self.client_socket.recv(PODTP_MAX_DATA_LEN + 1)
            if not data:
                print_t("Connection closed by the server.")
                return None
            
            self.process(data)
            try:
                return self.packet_queue.get_nowait()
            except queue.Empty:
                return None

    def process(self, data: bytes):
        for byte in data:
            match self.link_state:
                case WifiLinkState.PODTP_STATE_START_1:
                    if byte == PODTP_START_BYTE_1:
                        self.link_state = WifiLinkState.PODTP_STATE_START_2
                case WifiLinkState.PODTP_STATE_START_2:
                    if byte == PODTP_START_BYTE_2:
                        self.link_state = WifiLinkState.PODTP_STATE_LENGTH
                    else:
                        self.link_state = WifiLinkState.PODTP_STATE_START_1

                case WifiLinkState.PODTP_STATE_LENGTH:
                    self.length = byte
                    self.packet.length = 0
                    if self.length > PODTP_MAX_DATA_LEN or self.length == 0:
                        self.link_state = WifiLinkState.PODTP_STATE_START_1
                    else:
                        self.link_state = WifiLinkState.PODTP_STATE_RAW_DATA
                case WifiLinkState.PODTP_STATE_RAW_DATA:
                    self.packet.raw[self.packet.length] = byte
                    self.packet.length += 1
                    if self.packet.length == self.length:
                        self.link_state = WifiLinkState.PODTP_STATE_START_1
                        self.packet_queue.put(self.packet)