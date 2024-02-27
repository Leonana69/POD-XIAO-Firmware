import time, math
import struct

from podtp.podtp import Podtp
from podtp.podtp_packet import PODTP_MAX_DATA_LEN, PodtpPacket, PodtpType

PORT_LOAD_BUFFER = 1
PORT_WRITE_FLASH = 2
PAGE_SIZE = 1024

class LoadBuffer:
    def __init__(self):
        self.bufferPage = 0
        self.offset = 0

    def size(self):
        return struct.calcsize('<HH')

    def pack(self):
        return struct.pack('<HH', self.bufferPage, self.offset)
    
class WriteFlash:
    def __init__(self):
        self.bufferPage = 0
        self.flashPage = 0
        self.numPages = 0

    def size(self):
        return struct.calcsize('<HHH')

    def pack(self):
        return struct.pack('<HHH', self.bufferPage, self.flashPage, self.numPages)

# Set the server's IP address and port
# server_ip = '10.0.0.131'  # Replace with your ESP32's IP address
server_ip = '192.168.0.131'  # Replace with your ESP32's IP address
server_port = 80  # Replace with your ESP32's port number

podtp = Podtp(server_ip, server_port)
podtp.connect()

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()
    
def send_write_flash(flash_page, num_pages):
    return
    packet = PodtpPacket()
    packet.content.packet.header.type = PodtpType.PODTP_TYPE_BOOT_LOADER.value  # Set type (4 bits)
    packet.content.packet.header.port = PORT_WRITE_FLASH  # Set port (4 bits)

    write_flash = WriteFlash()
    write_flash.bufferPage = 0
    write_flash.flashPage = flash_page
    write_flash.numPages = num_pages

    packet.content.packet.data[:write_flash.size()] = write_flash.pack()
    packet.length = 1 + write_flash.size()
    message = packet.pack()
    client_socket.send(message)
    print(f'Sent write flash page {flash_page} num_pages {num_pages}')

def send_load_buffer():
    binary = read_binary_file('test.bin')
    packet = PodtpPacket()
    packet.content.packet.header.type = PodtpType.PODTP_TYPE_BOOT_LOADER.value  # Set type (4 bits)
    packet.content.packet.header.port = PORT_LOAD_BUFFER  # Set port (4 bits)

    load_buffer = LoadBuffer()

    max_packet_load = PODTP_MAX_DATA_LEN - load_buffer.size() - 1
    # max_packet_load = 15

    total_size = len(binary)
    # total_size = 15
    page_count = math.ceil(total_size / PAGE_SIZE)

    for index in range(0, total_size, max_packet_load):
        page = index // PAGE_SIZE
        offset = index % PAGE_SIZE

        if page % 10 == 0 and page > 0:
            send_write_flash(page - 10, 10)

        load_buffer.bufferPage = page % 10
        load_buffer.offset = offset
        packet.content.packet.data[:load_buffer.size()] = load_buffer.pack()
        # the last packet may not be full
        if offset + max_packet_load > total_size:
            packet_load = total_size - offset
        else:
            packet_load = max_packet_load
        packet.content.packet.data[load_buffer.size():load_buffer.size() + packet_load] = binary[offset:offset + packet_load]
        packet.length = 1 + load_buffer.size() + packet_load
        rslt = podtp.send_reliable(packet)
        print(f'Sent page {page} offset {offset} packet_length {packet.length} packet_load {packet_load} result {rslt}')
        time.sleep(0.1)

    send_write_flash(page // 10 * 10, page_count % 10)


podtp.send(PodtpPacket.GET_EMPTY_PACKET())
time.sleep(0.5)

# send one packet when key S is pressed
i = 0
while True:
    key = input()
    if key == 's':
        # Send data
        print(f'Sending packet {i}')
        send_load_buffer()
    elif key == 'q':
        break
    time.sleep(0.1)

podtp.disconnect()
