"""
printer.py

Shows message on the user's terminal.
"""
import sys
import datetime

# Color definitions
HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDCOLOR = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def timestamp():
    """
    Return formated timestamp.
    """
    return datetime.datetime.now().strftime("%H:%M:%S")


def info(text):
    """
    Print info message.
    """
    msg = "{c}{ts} {t} {ec}".format(c=BLUE,
                                    ts=timestamp(),
                                    t=text,
                                    ec=ENDCOLOR)
    print(msg)


def warning(text):
    """
    Print info message.
    """
    msg = "{c}{ts} {t} {ec}".format(c=YELLOW,
                                    ts=timestamp(),
                                    t=text,
                                    ec=ENDCOLOR)
    print(msg)


def error(text):
    """
    Print info message.
    """
    msg = "{c}{ts} {t} {ec}".format(c=RED,
                                    ts=timestamp(),
                                    t=text,
                                    ec=ENDCOLOR)
    print(msg)
    sys.exit(1)


def substep_info(text):
    """
    Print info message.
    """
    msg = "{c}.- {ts} {t} {ec}".format(c=BLUE,
                                       ts=timestamp(),
                                       t=text,
                                       ec=ENDCOLOR)
    print(msg)
