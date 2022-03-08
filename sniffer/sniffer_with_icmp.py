import ipaddress
import os
import socket
import struct
import sys

class IP:
    # IP structure used in other sniffer module
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

class ICMP:
    # ICMP struct built on the IP class
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type   =     header[0]
        self.code   =     header[1]
        self.sum    =      header[2]
        self.id     =       header[3]
        self.seq    =      header[4]

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
            # If the protocol is ICMP, use it
            if ip_header.protocol == "ICMP":
                # Print protocol and details about the host
                print('Protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
                print(f"Version {ip_header.ver}")
                print(f"Header length = {ip_header.ihl} TTL = {ip_header.ttl}")

                # Calculate where the IP header begins
                # .ihl field contains how many 4 byte chunks are in the header
                # Therefore, this field * 4 means we know how long the header is
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + 8]
                icmp_header = ICMP(buf)
                print(f"ICMP -> Type: {icmp_header.type} Code {icmp_header.code}")

    except KeyboardInterrupt:
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '160.39.234.194'
    sniff(host)
