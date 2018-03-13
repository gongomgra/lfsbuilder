
# Color definitions
HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDCOLOR = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def clockTime():
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")

def info(text):
    print BLUE + text + ENDCOLOR
    import time
    # time.sleep(5)

def warning(text):
    print YELLOW + clockTime() + " " + text + ENDCOLOR

def error(text):
    print RED + clockTime() + " " + text + ENDCOLOR
    import sys
    sys.exit(1)

def prettyPrint(element):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(element)

def substepInfo(text):
    text = "\_ " + clockTime() + " " + text
    info(text)
