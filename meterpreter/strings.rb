#
# Meterpreter script to run a linux-like 'strings' command on Windows
# Leverages sysinternals' strings.exe binary (http://technet.microsoft.com/en-us/sysinternals/bb897439.aspx).
# Provided by: Skyler Onken
#

@@exec_opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ],
  "-a" => [ false,"Ascii-only search."],
  "-b" => [ false,"Bytes of file to scan."],
  "-f" => [ false,"File offset at which to start scanning."],
  "-n" => [ false,"Minimum string length to print."],
  "-s" => [ false,"Recurse subdirectories."],
  "-o" => [ false,"Print offset string was located at."],
)

def usage
  print_line("Strings - Does strings for Windows")
  print_line("USAGE: run strings [options] [file]")
  print_line(@@exec_opts.usage)
  raise Rex::Script::Completed
end

@@exec_opts.parse(args) { |opt, idx, val|
  case opt
  when "-h"
    usage
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

unsupported if client.platform !~ /win32|win64/i

if unsupported
	print_line("Unsupported. If *nix, use native strings command.")
	raise Rex::Script::Completed
end

tmp = client.fs.file.expand_path("%TEMP%")

path = "#{tmp}\\strings.exe"

file_to_string = args.last

if not ::File.exists?(file_to_string)
  pwd = client.fs.dir.pwd
  file_to_string = "\"#{pwd}\\#{args[0]}\""
end

params_string = args[0...-1].join(" ")
full_params_string =  "-q #{params_string}"
full_arg_string = "#{file_to_string}"

client.fs.file.upload_file("#{path}","/usr/share/metasploit-framework/data/post/strings.exe")
cmd = "#{path} #{full_params_string} #{file_to_string}"
print_line(m_exec(client,cmd))

m_unlink(client, path)
