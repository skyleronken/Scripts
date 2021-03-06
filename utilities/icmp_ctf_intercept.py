#!/usr/bin/env python

#
# sudo iptables -A INPUT -p ICMP --icmp-type echo-request -j NFQUEUE --queue-num 1
#

from netfilterqueue import NetfilterQueue
from scapy.all import *
import sys

def send_echo_reply(pkt):
    ip = IP()
    icmp = ICMP()
    ip.src = pkt[IP].dst
    ip.dst = pkt[IP].src
    icmp.type = 0
    icmp.code = 0
    icmp.id = pkt[ICMP].id
    icmp.seq = pkt[ICMP].seq

    payload = str(pkt[ICMP].payload)

    secret = "iluvping"

    if secret not in payload:
        key = "this_is_the_first_key_try_to_find_the_next"
    else:
        key = "if_you_have_experienced_an_icmp_joke_ping_me"

    data_to_send = payload + key

    print "Sending back an echo reply to %s with key: '%s'" % (ip.dst,key)
    send(ip/icmp/Raw(load=data_to_send), verbose=0)
 
def process(payload):

    pkt = IP(payload.get_payload())

    proto = pkt.proto
 
    # Check if it is a ICMP packet
    if proto is 0x01:
        print "It's an ICMP packet"
        # Idea: intercept an echo request and immediately send back an echo reply packet
        if pkt[ICMP].type is 8:
            print "It's an ICMP echo request packet"
            send_echo_reply(pkt)
            payload.drop()
        else:
            payload.accept()

def main():
    q = NetfilterQueue()
    q.bind(1,process)
 
    try:
	print "Binding"
        #q.try_run()
        q.run()
    except KeyboardInterrupt:
        print "Exiting..."
        q.unbind()
        sys.exit(1)
 
main()
