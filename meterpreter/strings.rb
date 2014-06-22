opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ]
)

opts.parse(args) { |opt, idx, val|
  case opt
  when "-h"
    print_line("Strings - Does strings for Windows")
    print_line("Info is stored in " + ::File.join(Msf::Config.log_directory,"scripts", "strings"))
    print_line("USAGE: run strings [file]")
    print_line(opts.usage)
    raise Rex::Script::Completed
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

tmp = client.fs.file.expand_path("%TEMP%")

path = "#{tmp}\\strings.exe"

file_to_string = args[0]

if not ::File.exists?(file_to_string)
  pwd = client.fs.dir.pwd
  file_to_string = "\"#{pwd}\\#{args[0]}\""
end

client.fs.file.upload_file("#{path}","/usr/share/metasploit-framework/data/post/strings.exe")
cmd = "#{path} -q #{file_to_string}"
print_line(m_exec(client,cmd))

m_unlink(client, path)
