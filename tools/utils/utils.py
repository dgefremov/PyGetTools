import datetime


def print_log(message: str):
    print('[{0}] {1}'.format(datetime.datetime.now().time().strftime('%H:%M:%S'), message))


def hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000
