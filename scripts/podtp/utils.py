from typing import Union
import datetime

def print_t(*args, **kwargs):
    # Get the current timestamp
    current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    
    # Use built-in print to display the timestamp followed by the message
    print(f"[{current_time}]", *args, **kwargs)