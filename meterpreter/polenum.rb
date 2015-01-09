#
# Meterpreter script query windows registry settings to determine recent user activity.
# Provided by: Skyler Onken
#

# Meterpreter Session
@client = client

@@exec_opts = Rex::Parser::Arguments.new(
  "-h" => [ false,"Help menu." ],
  "" => [ false,""],
)

def usage
  print_line("polenum - pattern of life enumeration tool for current windows user (HKCU).")
  print_line("USAGE: run grepstat [options]")
  print_line(@@exec_opts.usage)
  raise Rex::Script::Completed
end

if client.platform !~ /win32|win64/i
    print_line("Unsupported. This is a windows only script!")
	raise Rex::Script::Completed
end

def reg_getvaldata(key,valname)
	v = nil
	begin
		root_key, base_key = client.sys.registry.splitkey(key)
		open_key = client.sys.registry.open_key(root_key, base_key, KEY_READ)
		v = open_key.query_value(valname).data
		open_key.close
	rescue
		print_error("Error opening key!")
	end
	return v
end

begin

	reg_owner = reg_getvaldata("HKLM\\software\\microsoft\\windows nt\\currentversion","RegisteredOwner")
	print_line("Registered Owner: #{reg_owner}")

	recent_run = reg_getvaldata("HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\runmru","MRUList")
	recent_run.split("").each do |i|
		cur_rec_run = reg_getvaldata("HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\runmru",i)
		print_line("#{cur_rec_run}")
	end
end

#- URLS
#reg enumkey -k "HKCU\\Software\\microsoft\\internet explorer\\typedurls"
#reg queryval -k "HKCU\\Software\\microsoft\\internet explorer\\typedurls" -v url1

#- PREFETCH
#reg queryval -k "HKLM\\system\\currentcontrolset\\control\\session manager\\memory management\\prefetchparameters" -v EnablePrefetcher

#- Most recent RUN command
#reg enumkey -k "HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\runmru"
#reg queryval -k "HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\runmru" -v "MRUList"

#- Most recent viewed DOCUMENTS
#reg enumkey -k "HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\recentdocs"
#reg enumkey -k "HKCU\\software\\microsoft\\windows\\currentversion\\explorer\\comdlg32"

