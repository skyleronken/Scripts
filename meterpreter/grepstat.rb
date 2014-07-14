#
# Meterpreter script to 'grep' the output of Windows netstat.
# Provided by: Skyler Onken
#

@@exec_opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ],
  "-a" => [ false,"Display all active connections."],
  "-n" => [ false,"Display connections without resolving names."],
  "-o" => [ false,"Display PID associated with connection."],
  "-p" => [ true,"Shows connections for the specified protocol [tcp,udp,icmp,ip,tcpv6,udpv6,icmpv6,ipv6]"], 
  "-r" => [ false,"Display routing table"]
)

def usage
  print_line("grepstat - greps windows netstat output")
  print_line("USAGE: run grepstat [options] [search_string]")
  print_line(@@exec_opts.usage)
  raise Rex::Script::Completed
end

if client.platform !~ /win32|win64/i
  print_line("Unsupported. If *nix, use native strings command.")
  raise Rex::Script::Completed
end

search_string = args.last

netstat_args = ""
findstr_args = ""

@@exec_opts.parse(args) { |opt, idx, val|
  case opt
  when "-h"
    usage
  when "-a"
    netstat_args << "-a "
  when "-n"
    netstat_args << "-n "
  when "-o"
    netstat_args << "-o "
  when "-r"
    netstat_args << "-r "
  when "-p"
    netstat_args << "-p #{val} "
  when "-b"
    findstr_args << "/b "
  when "-e"
    findstr_args << "/e "
  when "-l"
    findstr_args << "/l "
  when "-x"
    findstr_args << "/r "
  when "-i"
    findstr_args << "/i "
  when "-y"
    findstr_args << "/x "
  when "-v"
    findstr_args << "/v "
  end
}

require 'fileutils'

def m_unlink(client, path)
  r = client.sys.process.execute("cmd.exe /c del /F /S /Q " + path, nil, {'Hidden' => 'true'})
  while(r.name)
    select(nil, nil, nil, 0.10)
  end
  r.close
end

# Exec a command and return the results
def m_exec(client, cmd)
  begin
    r = client.sys.process.execute(cmd, nil, {'Hidden' => true, 'Channelized' => true})
    b = ""
    while(d = r.channel.read)
      b << d
      break if d == ""
    end
    r.channel.close
    r.close
    b
  rescue ::Exception => e
    print_error("Failed to run command #{cmd}")
    print_error("Error: #{e.class} #{e}")
  end
end

host,port = client.session_host, client.session_port

cmd = "netstat #{netstat_args}"
netstat = m_exec(client,cmd)

netstat = netstat.lines.map(&:chomp)

for line in netstat
  if line.include? "#{search_string}"
    print_line(line)
  end
end

m_unlink(client, path)
