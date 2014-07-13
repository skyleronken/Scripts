#
# Meterpreter script to hash a file on the remote system
# Provided by: Skyler Onken
#

@@exec_opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ]
)

def usage
  print_line("hash_file - Will hash a file")
  print_line("USAGE: run hash_file [file]")
  print_line(@@exec_opts)
  raise Rex::Script::Completed
end


@@exec_opts.parse(args) { |opt, idx, val|
  case opt
  when "-h"
    usage
  end
}

require 'fileutils'


begin 
	hashdata_md5 = client.fs.file.md5(args.last).unpack("H*")
	hashdata_sha1 = client.fs.file.sha1(args.last).unpack("H*")

	print_line("MD5   : #{hashdata_md5}")
	print_line("SHA-1 : #{hashdata_sha1}")

rescue
	print_error("File \"#{args.last}\" not found!")

end