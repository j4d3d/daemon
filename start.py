import os

if True:
    print('Deleting DB')
    try:
        os.remove('data/Upwork.json')
    except OSError:
        pass

import time
import helper
import traceback
from termcolor import colored as col

import util.logger
from util.logger import log, log_exception

os.system('cls' if os.name == 'nt' else 'clear')
log("Starting")

from daemon import Daemon
daemon = Daemon()

# encapsulate everything in try/catch
try:

    # None.crash() # ooh a paradox

    log("Starting daemon")
    daemon.start()

except Exception as ex:

    log_exception(ex)

    # traceback.print_exception(type(ex), ex, ex.__traceback__)
    # log(col('Something went wrong with Daemon, quitting. >:(', 'red'))
    # log(col('Daemon crashed, sleeping it off...', 'grey'))
    # for i in range(0,3):
    #     log(col('zzz', 'grey'))
    #     time.sleep(1)

# helper.wait_for_arrow(1)

daemon.quit()
log("Program finished.")
util.logger.dispose()