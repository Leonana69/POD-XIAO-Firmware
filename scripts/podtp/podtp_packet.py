from ctypes import *
from enum import Enum

PODTP_MAX_DATA_LEN = 127

PODTP_START_BYTE_1 = 0xAD
PODTP_START_BYTE_2 = 0x6E

class PodtpType(Enum):
    PODTP_TYPE_ERROR = 0x0
    PODTP_TYPE_ACK = 0x1
    PODTP_TYPE_BOOT_LOADER = 0xF

class Header(Union):
    _fields_ = [("header", c_uint8),
                ("_bitfield", c_uint8)]

    @property
    def type(self):
        return (self._bitfield & 0xF0) >> 4

    @type.setter
    def type(self, value):
        self._bitfield = (self._bitfield & 0x0F) | ((value & 0x0F) << 4)

    @property
    def port(self):
        return self._bitfield & 0x0F

    @port.setter
    def port(self, value):
        self._bitfield = (self._bitfield & 0xF0) | (value & 0x0F)

class DataPacket(Structure):
    _pack_ = 1  # Ensure packed structure (no padding)
    _fields_ = [("header", Header),
                ("data", c_uint8 * PODTP_MAX_DATA_LEN)]

class ContentPacket(Union):
    _fields_ = [("packet", DataPacket),
                ("raw", c_uint8 * (PODTP_MAX_DATA_LEN + 1))]
    
class PodtpPacket(Structure):
    _fields_ = [("length", c_uint8),
                ("content", ContentPacket)]
    
    def pack(self):
        buffer = bytearray(2 + 1 + self.length)
        buffer[0] = PODTP_START_BYTE_1
        buffer[1] = PODTP_START_BYTE_2
        buffer[2] = self.length
        buffer[3:3 + self.length] = self.content.raw[:self.length]
        return buffer
    
    def unpack(self, buffer):
        if buffer[0] != PODTP_START_BYTE_1 or buffer[1] != PODTP_START_BYTE_2:
            return False
        self.length = buffer[2]
        self.content.raw[:self.length] = buffer[3:3 + self.length]
        return True
    
    def GET_EMPTY_PACKET():
        packet = PodtpPacket()
        packet.length = 0
        return packet
    
    def __repr__(self):
        return f'PodtpPacket(length={self.length}, type={self.content.packet.header.type}, port={self.content.packet.header.port})'