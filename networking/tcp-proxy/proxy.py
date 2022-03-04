import sys
import socket
import threading

HEX_FILTER = ''.join([len(repr(chr(i)) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isInstance(src, bytes):
        src = src.decode()

    results = list()

    for i in range(0, len(src), length):
        word = str(src[])
