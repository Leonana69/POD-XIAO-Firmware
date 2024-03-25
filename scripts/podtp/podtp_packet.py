from enum import Enum

PODTP_MAX_DATA_LEN = 126

PODTP_START_BYTE_1 = 0xAD
PODTP_START_BYTE_2 = 0x6E

class PodtpType(Enum):
    PODTP_TYPE_ACK = 0x1
    PODTP_TYPE_COMMAND = 0x2
    PODTP_TYPE_LOG = 0x3
    PODTP_TYPE_ESP32 = 0xE
    PODTP_TYPE_BOOT_LOADER = 0xF
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, int):
            __value = PodtpType(__value)
        return super().__eq__(__value)

class PodtpPort(Enum):
    # PODTP_TYPE_ACK
    PORT_ERROR = 0x0
    PORT_OK = 0x1

    # PODTP_TYPE_COMMAND
    PODTP_PORT_RPYT = 0x0
    PODTP_PORT_TAKEOFF = 0x1
    PODTP_PORT_LAND = 0x2

    # PODTP_TYPE_LOG
    PODTP_PORT_STRING = 0x0
    
    # PODTP_TYPE_ESP32
    PORT_ECHO = 0x0
    PORT_START_STM32_BOOTLOADER = 0x1
    PORT_START_STM32_FIRMWARE = 0x2
    PORT_DISABLE_STM32 = 0x3
    PORT_ENABLE_STM32 = 0x4

    # PODTP_TYPE_BOOT_LOADER
    PORT_LOAD_BUFFER = 0x1
    PORT_WRITE_FLASH = 0x2

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, int):
            __value = PodtpPort(__value)
        return super().__eq__(__value)

PACKET_TYPE_NAMES = {
    PodtpType.PODTP_TYPE_ACK.value: 'ACK',
    PodtpType.PODTP_TYPE_COMMAND.value: 'COMMAND',
    PodtpType.PODTP_TYPE_LOG.value: 'LOG',
    PodtpType.PODTP_TYPE_ESP32.value: 'ESP32',
    PodtpType.PODTP_TYPE_BOOT_LOADER.value: 'BOOT_LOADER'
}

class RawPacket:
    def __init__(self, length = 1) -> None:
        if length > PODTP_MAX_DATA_LEN + 1 or length < 1:
            raise ValueError("Length must be between 1 and PODTP_MAX_DATA_LEN + 1")
        self.length = length
        self.raw = bytearray(PODTP_MAX_DATA_LEN + 1)
    
    def __getitem__(self, key):
        return self.raw[key]

    def __setitem__(self, key, value):
        self.raw[key] = value

    def __len__(self):
        return self.length

    def unpack(self, buffer):
        self.length = buffer[0]
        self.data = buffer[1:]

class PodtpPacket:
    class Header:
        def __init__(self, buffer: bytearray) -> None:
            self.buffer = buffer

        @property
        def type(self):
            return (self.buffer[0] & 0xF0) >> 4
        
        @type.setter
        def type(self, value: int | PodtpType):
            if isinstance(value, PodtpType):
                value = value.value
            self.buffer[0] = (self.buffer[0] & 0x0F) | ((value & 0x0F) << 4)
        
        @property
        def port(self):
            return self.buffer[0] & 0x0F
        
        @port.setter
        def port(self, value: int | PodtpPort):
            if isinstance(value, PodtpPort):
                value = value.value
            self.buffer[0] = (self.buffer[0] & 0xF0) | (value & 0x0F)

    class Data:
        def __init__(self, buffer: bytearray) -> None:
            self.buffer = buffer

        def __getitem__(self, key):
            if isinstance(key, slice):
                start = key.start + 1 if key.start is not None else 1
                stop = key.stop + 1 if key.stop is not None else len(self.buffer)
                return self.buffer[start:stop]
            else:
                return self.buffer[key + 1]
        
        def __setitem__(self, key, value):
            if isinstance(key, slice):
                start = key.start + 1 if key.start is not None else 1
                stop = key.stop + 1 if key.stop is not None else len(self.buffer)
                self.buffer[start:stop] = value
            else:
                self.buffer[key + 1] = value

    def __init__(self) -> None:
        self.length = 0
        self.raw = RawPacket()
        self.header = PodtpPacket.Header(self.raw)
        self.data = PodtpPacket.Data(self.raw)

    def set_header(self, type: int | PodtpType, port: int | PodtpPort) -> 'PodtpPacket':
        self.header.type = type
        self.header.port = port
        self.length = 1
        return self

    def pack(self) -> bytearray:
        buffer = bytearray(2 + 1 + self.length)
        buffer[0] = PODTP_START_BYTE_1
        buffer[1] = PODTP_START_BYTE_2
        buffer[2] = self.length
        buffer[3:3 + self.length] = self.raw[:self.length]
        return buffer
    
    def unpack(self, buffer) -> bool:
        if buffer[0] != PODTP_START_BYTE_1 or buffer[1] != PODTP_START_BYTE_2:
            return False
        self.length = buffer[2]
        self.raw[:self.length] = buffer[3:3 + self.length]
        return True

    def __repr__(self):
        return f'PodtpPacket(length={self.length}, type={PACKET_TYPE_NAMES[self.header.type]}, port={self.header.port})'