import socket
import select
import time
from enum import Enum
from typing import Optional

from .podtp_packet import *
from .utils import print_t

LINK_MAX_WAIT_TIME = 200

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

    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            print_t(f'Connected to {self.server_ip}:{self.server_port}')
        except:
            print_t(f'Failed to connect to {self.server_ip}:{self.server_port}')

    def disconnect(self):
        self.client_socket.close()
        print_t(f'Disconnected from {self.server_ip}:{self.server_port}')

    def send(self, packet: PodtpPacket):
        self.client_socket.send(packet.pack())

    def receive(self) -> Optional[PodtpPacket]:
        """
        Read from the TCP connection until a packet is returned, or a timeout occurs.
        :param timeout: The number of seconds to wait for a complete packet.
        :return: A PodtpPacket if one is successfully received, None otherwise.
        """
        while True:
            readable, _, _ = select.select([self.client_socket], [], [], 5)
            if not readable:
                print_t("Timeout: No data received.")
                return None

            data = self.client_socket.recv(PODTP_MAX_DATA_LEN + 1)
            if not data:
                print_t("Connection closed by the server.")
                return None
            
            packet = self.process(data)
            if packet:
                return packet

    def process(self, data: bytes) -> Optional[PodtpPacket]:
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
                    self.packet.content.raw[self.packet.length] = byte
                    self.packet.length += 1
                    if self.packet.length >= self.length:
                        self.link_state = WifiLinkState.PODTP_STATE_START_1
                        return self.packet
        return None