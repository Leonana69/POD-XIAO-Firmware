import json
from podtp import Podtp, print_t

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if not podtp.send_ctrl_lock(False):
            print_t('Failed to unlock control')
        else:
            print_t('Drone unlocked')
            podtp.send_command_setpoint(0, 0, 0, 12430)
            podtp.send_command_hover(0.5, 0, 0, 0)
        podtp.disconnect()

if __name__ == '__main__':
    main()