#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os

prefix = "https://login.ezproxy.yorksj.ac.uk/login?url=";

for subdir, dirs, files in os.walk("SRC"):
    for f in files:
		print "Ouverture de %s" % f
		reader = MARCReader(open("SRC/%s" % f), force_utf8=True);
		out = open("OUT/%s-auth.mrc" % os.path.splitext(f)[0], 'wb');
		nb = 0
		for record in reader:
			try:
				#print record["001"]
				pass
			except:
				print "\tError while decoding [%s]" % nb
			nb += 1
			
			for f856 in record.get_fields("856"):
				if len(f856.get_subfields('u')) != 1:
					print "Wrong number of 856u"
				else:
					url = "%s%s" % (prefix, f856.get_subfields('u')[0])
					f856.delete_subfield("u")
					f856.add_subfield("u", url)
					f856.add_subfield("z", "Click here to access electronic holdings.")
			out.write(record.as_marc())
		print "Updated %s file: %s" % (f, nb)
