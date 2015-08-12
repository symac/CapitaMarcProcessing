#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib

prefix = "https://journalarchives.jisc.ac.uk/Shibboleth.sso/Login?entityID=https%3A%2F%2Fidp.yorksj.ac.uk%2Foala&target="

for subdir, dirs, files in os.walk("."):
	if subdir == "./OUT": continue
	for f in [fi for fi in files if fi.endswith(".mrc")]:
		filename = os.path.join(subdir,f)
		print "# # # # # # # # # # # #"
		print "Reading: %s" % filename
		reader = MARCReader(open("%s" % filename), force_utf8=True);
		
		outputFilename = "OUT/%s" % os.path.basename(filename)
		print "Output:  %s" % outputFilename
		out = open(outputFilename, 'wb');
		nb = 0
		for record in reader:
			nb += 1

			for f856 in record.get_fields("856"):
				if len(f856.get_subfields('u')) != 1:
					print "Wrong number of 856u"
					exit()
				else:
					url = "%s%s" % (prefix, urllib.quote_plus(f856.get_subfields('u')[0]))
					f856.delete_subfield("u")
					
					# We need to remove the existing $z
					f856.delete_subfield("z")
					f856.add_subfield("u", url)
					f856.add_subfield("z", "Click here to access electronic holdings.")
			out.write(record.as_marc())
		print "%s records in file" % nb
		print ""