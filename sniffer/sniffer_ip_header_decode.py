import ipaddress
import struct
import os
import socket
import sys

class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        self.ver = header[0] >> 4       # only want the high order bits or the first "nybble" right shift (shr) will make the unwanted bits fall off
        self.ihl = header[0] & 0xF      # to get the second nybble AND against 00001111 (0xF)

        self.tos    =   header[1]
        self.len    =   header[2]
        self.id     =   header[3]
        self.offset =   header[4]
        self.ttl    =   header[5]
        self.protocol_num = header[6]
        self.sum    =   header[7]
        self.src    =   header[8]
        self.dst    =   header[9]

        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print('%s No protocol for %s ' % (e, self.protocol_num))

def sniff(host):
    # Similar to the sniffer in udp_hd.py
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET,
                            socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host,0))
    # Include ip headers in the captures
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        # Loop to recieve packets
        while True:
            # Read a packet
            raw_buffer = sniffer.recvfrom(65535)[0]
            # Create an IP header from the frist 20 bytes
            ip_header = IP(raw_buffer[0:20])
            # Print the detected protocol and hosts
            print('Protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        print("Usage = python sniffer_ip_header_decode.py IP")
        sys.exit(0)
    sniff(host)

