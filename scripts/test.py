import socket
import time

from podtp import PodtpPacket



# Set the server's IP address and port
server_ip = '10.0.0.131'  # Replace with your ESP32's IP address
server_port = 80  # Replace with your ESP32's port number

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

packet = PodtpPacket()
packet.content.packet.header.type = 15  # Set type (4 bits)
packet.content.packet.header.port = 1  # Set port (4 bits)
packet.content.packet.data[0] = 0x01  # Set data
packet.content.packet.data[1] = 0x02  # Set data
packet.content.packet.data[2] = 0x04  # Set data
packet.length = 4  # Set length

try:
    # Connect to the server
    client_socket.connect((server_ip, server_port))
    print(f'Connected to {server_ip}:{server_port}')

    # Send data
    message = PodtpPacket.GET_EMPTY_PACKET().pack()
    client_socket.send(message)
    time.sleep(1)

    # send one packet when key S is pressed
    i = 0
    while True:
        key = input()
        if key == 's':
            # Send data
            print(f'Sending packet {i}')
            packet.content.packet.data[0] = i
            i += 1
            message = packet.pack()
            client_socket.send(message)
        elif key == 'q':
            break
        time.sleep(0.1)
finally:
    # Close the connection
    client_socket.close()
    print('Connection closed')
