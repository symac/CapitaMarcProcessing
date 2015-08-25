#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, codecs

prefix = "https://login.ezproxy.yorksj.ac.uk/login?url=";

from pymarc import MARCReader, marc8_to_unicode
import sys

nb = 0

class ExceptionHandlingIterator(object):
	def __init__(self, iterable):
		self._iter = iter(iterable)
		self.handlers = []
	
	def __iter__(self):
		return self

	def next(self):
		global nb
		try:
			return self._iter.next()
		except StopIteration as e:
			raise e
		except ValueError as e:
			sys.stderr.write("## encoding error ##\n")
			return self.next()
		except Exception as e:
			print "####"
			print type(e)
			return self.next()

for subdir, dirs, files in os.walk("SRC"):
    for f in [fi for fi in files if fi.endswith(".mrc")]:
		with open("SRC/%s" % f, 'rb') as fh:
			reader = ExceptionHandlingIterator(MARCReader(fh, force_utf8=True, utf8_handling='ignore', to_unicode=True))
			out = codecs.open("OUT/%s-auth.mrc" % os.path.splitext(f)[0], 'wb', 'utf8');
			nb = 0
			for record in reader:
				# print record["001"]
				nb += 1
				
				for f856 in record.get_fields("856"):
					if len(f856.get_subfields('u')) != 1:
						print "Wrong number of 856u"
					else:
						url = "%s%s" % (prefix, f856.get_subfields('u')[0])
						f856.delete_subfield("u")
						f856.add_subfield("u", url)
						f856.add_subfield("z", "View eBook online.")
					out.write(record.as_marc())
			print "Updated %s file: %s" % (f, nb)
