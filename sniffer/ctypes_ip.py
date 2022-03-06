from ctypes import *
import socket
import struct

class IP(Structure):
    _fields_=[
        ("version",     c_ubyte,        4),
        ("ihl",         c_ubyte,        4),
        ("tos",         c_ubyte,        8),
        ("len",         c_ushort,       16),
        ("id",          c_ushort,       16),
        ("offset",      c_ushort,       16),
        ("ttl",         c_ubyte,        8),
        ("protocol_num",c_ubyte,        8),
        ("sum",         c_ushort,       16),
        ("src",         c_uint32,       32),
        ("dst",         c_uint32,       32),
    ]

def __new__(cls, socket_buffer=None):
    return cls.from_buffer_copy(socket_buffer)

def __init__(self, socket_buffer = None):
    self.src_addresss = socket.inet_ntoa(struct.pack("<L", self.src))
    self.dst_addresss = socket.inet_ntoa(struct.pack("<L", self.dst))
