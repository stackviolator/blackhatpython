import ipaddress
import os
import socket
import struct
import sys
import threading
import time

SUBNET = input("Enter subnet in CIDR: ")
MESSAGE = 'pls no detect am college student'

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

def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf-8'), str(ip), 62342)

class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        if os.name == "nt":
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = set([f"{str(self.host)} *"])
        try:
            while True:
                # Read a single packet
                raw_buffer = self.socket.recvfrom(65535)[0]
                # create an IP header from the first 20 bytes
                # Create an IP header from the frist 20 bytes
                ip_header = IP(raw_buffer[0:20])
                # If the protocol is ICMP, use it
                if ip_header.protocol == "ICMP":
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            # Make sure the packet has the message
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf-8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in self.hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f"Host up @ {ip_header.src_address}")
        except KeyboardInterrupt:
            if os.name == "nt":
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print('\n User interrupted')
            if hosts_up:
                print(f"Hosts on {SUBNET}")
                for host in hosts_up:
                    print(f"{host}")
                print("")
                sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        # Need to manually change, this is my IP in the Columbia U network
        host = '160.39.234.152'

    s = Scanner(host)
    time.sleep(5)
    print("Setting up threading... ")
    t = threading.Thread(target=udp_sender)
    print("Thread started... ")
    t.start()
    print("Sniffing... ")
    s.sniff()
