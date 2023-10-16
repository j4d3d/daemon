import time
import keyboard
from termcolor import colored as col

from util.logger import log

def wait_for_arrow():
    return True
    log(col('Awaiting keyboard... (ctrl -> to continue, ctrl <- to stop)', 'grey'))
    while True:
        time.sleep(0.05)
        if (keyboard.is_pressed('ctrl+left')):
            return False
        elif keyboard.is_pressed('ctrl+right'):
            return True