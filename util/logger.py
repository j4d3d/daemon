import os
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
clear()

import sys
import re
import math

import traceback
from termcolor import colored as col

from datetime import datetime

CLOSE_AFTER_WRITE = True

if not os.path.exists('logs'):
    os.makedirs('logs')

loggers = {}

ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def strip_ansi_escape_sequences(text):
    return ansi_escape_pattern.sub('', text)

class Logger:
    def __init__(self, key):
        self.key = key
        loggers[key] = self

        self.file = None
        self.filename = f"logs/log_{key}_{math.floor(datetime.now().timestamp())}.txt"
        if not CLOSE_AFTER_WRITE:
            self.file = open(self.filename, 'w', encoding='utf-8')
    
    def log(self, text):
        text = str(text)
        _text = text
        if ansi_escape_pattern.match(_text) is None:
            _text = col(_text, "grey")
        # _text = col(f"log_{self.key}: ", "grey") + f"{_text}"
        print(_text)

        stripped = strip_ansi_escape_sequences(text) + "\n"
        if CLOSE_AFTER_WRITE:
            self.file = open(self.filename, "a", encoding='utf-8')
            self.file.write(stripped)
            self.file.close()
        else: 
            self.file.write(stripped)
    
    def dispose(self):
        self.file.close()

def log(text, key="default"):
    logger = None
    if key in loggers:
        logger = loggers[key]
    else:
        logger = Logger(key)
        loggers[key] = logger
    logger.log(text)

def log_exception(ex):
    exception_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
    
    log('')
    for i in range(0, 4): caution_line()
    log('')

    lines_code = []
    lines_stack = []

    for line in exception_lines:
        line = line.strip()
        if '\n' in line:
            index = line.index('\n')
            lines_code.append(line[:index])
            lines_stack.append(line[index+1:])
            # print('line: '+line)
    
    log(col('\nStack:', 'white'))
    for line in lines_stack:
        log(line.strip())
    
    log(col('\nCode:', 'white'))
    for line in lines_code:
        log(line.strip())

    log(col('\nException:', 'white'))
    # log(sys.exc_info()[2])
    # log(traceback.format_exc())
    log(col(exception_lines[-1].strip(), 'magenta'))
    log(lines_code[-1].strip())
    log(lines_stack[-1].strip())
    
    log('')
    for i in range(0, 4): caution_line()
    log('')

symbols = '.coCODco.,'
colors = ['red', 'light_red', 'light_yellow', 'green', 'blue', 'cyan', 'magenta']
caution_phase_symbol = 0
caution_phase_color = 0

def caution_line(length=64):
    global caution_phase_symbol
    global caution_phase_color
    caution_line = ''
    for i in range(0, length):
        caution_phase_symbol = (caution_phase_symbol + 1) % len(symbols)
        caution_phase_color = (caution_phase_color + 1) % len(colors)
        caution_line += col(symbols[caution_phase_symbol], colors[caution_phase_color])
    log(caution_line)

def dispose():
    log("Closing Logger files")
    for key, logger in loggers.items():
        logger.dispose()

def print_head_tail(text, LINE_WIDTH=96, LINE_COUNT=2):
    printout = ''
    
    tail_end = len(text)
    tail_start = tail_end - LINE_COUNT * LINE_WIDTH
    
    head_start = 0
    head_end = LINE_COUNT * LINE_WIDTH
    
    # collapse head/tail ranges to fit text
    if (head_end > tail_end):
        head_end = tail_end
        tail_start = tail_end

    if (tail_start < head_end): 
        tail_start = head_end
    
    head = text[head_start:head_end]
    tail = text[tail_start:tail_end]

    line = 'description: '
    for body in [head, tail]:
        index = 0
        lines = 0
        while index < len(body) and lines < LINE_COUNT:
            append_size = LINE_WIDTH - len(line)
            ceil = index + append_size
            ceil = min(ceil, len(body))
            
            line += body[index:ceil]
            printout += '\n' + line

            index += append_size
            lines += 1
            line = ''
        
        # print 
        
        symbol = '~'

        if body == head: 
            symbol = '.'
            if len(tail) == 0:  continue

        printout += '\n'
        for i in range(0, LINE_WIDTH):
            printout += symbol

    # desc = desc_flat[0:48] + "...." + desc[-48:]
    log(f"{printout}")

# colors = ["red", "grey", "blue", "magenta"]
# parts = []
# pattern = "("
# for color in colors:
#     parts.append(re.escape(col("UWU", color).replace("UWU",".*")))
# pattern += "|".join(parts) + ")"
# re_clean = re.compile(pattern)
# log(f"Logger escape pattern: {pattern}")