import math, time
import struct
import argparse
from tqdm import tqdm

from podtp import Podtp
from podtp import PodtpPacket, PodtpType, PodtpPort
from podtp import print_t
from podtp.podtp_packet import PODTP_MAX_DATA_LEN

# Set the server's IP address and port
DEFAULT_SERVER_IP = '10.0.0.115'  # Replace with your ESP32's IP address
# DEFAULT_SERVER_IP = '192.168.0.116'  # Replace with your ESP32's IP address
DEFAULT_SERVER_PORT = 80  # Replace with your ESP32's port number

FIRMWARE_START_PAGE = 128
BUFFER_PAGE_COUNT = 10
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

def read_bin_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def send_write_flash(podtp, flash_page, num_pages) -> bool:
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_BOOT_LOADER,
                                      PodtpPort.PORT_WRITE_FLASH)
    write_flash = WriteFlash()
    write_flash.bufferPage = 0
    write_flash.flashPage = flash_page + FIRMWARE_START_PAGE
    write_flash.numPages = num_pages

    packet.data[:write_flash.size()] = write_flash.pack()
    packet.length = 1 + write_flash.size()
    if not podtp.send(packet):
        print_t(f'Failed to write flash page {flash_page}')
        return False
    return True

def send_load_buffer(podtp, file_path) -> bool:
    binary = read_bin_file(file_path)
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_BOOT_LOADER,
                                      PodtpPort.PORT_LOAD_BUFFER)

    load_buffer = LoadBuffer()

    max_packet_load = PODTP_MAX_DATA_LEN - load_buffer.size() - 1

    total_size = len(binary)
    page_count = math.ceil(total_size / PAGE_SIZE)
    buffer_free_size = BUFFER_PAGE_COUNT * PAGE_SIZE

    print_t(f'Uploading {page_count} pages with {math.ceil(total_size / max_packet_load)} packets...')
    index = 0
    pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc='Uploading')
    while index < total_size:
        page = index // PAGE_SIZE
        offset = index % PAGE_SIZE

        if buffer_free_size == 0:
            if not send_write_flash(podtp, page - 10, 10):
                return False
            buffer_free_size = BUFFER_PAGE_COUNT * PAGE_SIZE

        load_buffer.bufferPage = page % 10
        load_buffer.offset = offset
        packet.data[:load_buffer.size()] = load_buffer.pack()
        # the last packet may not be full
        if index + max_packet_load > total_size:
            packet_load = total_size - index
        else:
            packet_load = max_packet_load

        if packet_load > buffer_free_size:
            packet_load = buffer_free_size

        buffer_free_size -= packet_load
        pbar.update(packet_load)

        # print_t(f'Sent page {page} offset {offset} packet_length {packet.length} packet_load {packet_load}')
        packet.data[load_buffer.size():load_buffer.size() + packet_load] = binary[index:index + packet_load]
        packet.length = 1 + load_buffer.size() + packet_load
        if not podtp.send(packet):
            print_t(f'Upload failed at page {page} offset {offset}')
            return False
        index += packet_load

    if not send_write_flash(podtp, page // 10 * 10, page_count % 10):
        return False
    return True

def start_stm32_bootloader(podtp):
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32,
                                      PodtpPort.PORT_START_STM32_BOOTLOADER)
    podtp.send(packet)

def start_stm32_firmware(podtp):
    packet = PodtpPacket().set_header(PodtpType.PODTP_TYPE_ESP32,
                                      PodtpPort.PORT_START_STM32_FIRMWARE)
    podtp.send(packet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload firmware to STM32 via ESP32 over WiFi')
    parser.add_argument('file', help='Binary file to upload', type=str)
    parser.add_argument('-i', '--ip', help='IP address of the ESP32', type=str, default=DEFAULT_SERVER_IP, required=False)
    parser.add_argument('-p', '--port', help='Port number of the ESP32', type=int, default=DEFAULT_SERVER_PORT, required=False)

    args = parser.parse_args()
    print_t(f'Uploading {args.file} to {args.ip}:{args.port}')

    podtp = Podtp(args.ip, args.port)
    if not podtp.connect():
        exit(1)

    start_stm32_bootloader(podtp)
    time.sleep(1)
    if send_load_buffer(podtp, args.file):
        print_t('Upload [OK]')
        start_stm32_firmware(podtp)
    else:
        print_t('Upload [FAILED]')
    podtp.disconnect()