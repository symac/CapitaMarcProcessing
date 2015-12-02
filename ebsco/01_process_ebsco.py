#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib
from os import listdir
from os.path import isfile, join
import sys

nb_total = 0
nb_total_new = 0

prefix = "http://ezproxy.yorksj.ac.uk/login?url=";

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
			return self.next()
		except Exception as e:
			print "####"
			print type(e)
			return self.next()

# We need to clean the TMP file first
tmpFiles = [ f for f in listdir("TMP") if isfile(join("TMP",f)) ]
for f in tmpFiles:
	os.remove(join("TMP",f))
	print "Cleaning TMP: %s" % f
			
'''
This file will process the askews files to remove any 020 that is not for an ebook
'''
f001done = {}
for subdir, dirs, files in os.walk("SRC"):
	for f in sorted([fi for fi in files if fi.endswith(".mrc") or fi.endswith(".bin")], reverse=True):
		print f
		filename = os.path.join(subdir,f)
		print "# # # # # # # # # # # #"
		print "Reading: %s" % filename

		fh = open(filename, 'rb')
		reader = ExceptionHandlingIterator(MARCReader(fh, force_utf8=True, utf8_handling='ignore', to_unicode=True))
		
		outputFilename = "TMP/%s-clean.mrc" % os.path.splitext(f)[0]
		out = open(outputFilename, 'wb');
		nb = 0
		nb_new = 0
		for record in reader:
			nb += 1
			f001 = record.get_fields("001")[0].data
			if f001 in f001done:
				# print "Skipping %s, already done in %s" % (f001, f001done[f001])
				pass
			else:
				nb_new += 1
				f001done[f001] = f
				
				for f856 in record.get_fields("856"):
					if len(f856.get_subfields('u')) != 1:
						print "Wrong number of 856u"
					else:
						url = "%s%s" % (prefix, f856.get_subfields('u')[0])
						f856.delete_subfield("u")
						f856.add_subfield("u", url)
						f856.add_subfield("z", "View eBook online.")
						out.write(record.as_marc())
		
		nb_total += nb
		nb_total_new += nb_new
		print "%s records in file [%s new]" % (nb, nb_new)
		out.close()

print "\n\nTotal records: %s # Unique records: %s" % (nb_total, nb_total_new)
os.chdir("TMP")
os.system("mergeFiles.py -o mergedFile.mrc")