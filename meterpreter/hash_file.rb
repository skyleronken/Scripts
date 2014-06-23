opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ]
)

opts.parse(args) { |opt, idx, val|
  case opt
  when "-h"
    print_line("hash_file - Will hash a file")
    print_line("Info is stored in " + ::File.join(Msf::Config.log_directory,"scripts", "hash_file"))
    print_line("USAGE: run hash_file [options] [file]")
    print_line(opts.usage)
    raise Rex::Script::Completed
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