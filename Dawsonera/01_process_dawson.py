#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode, record
import os, urllib
import sys
nb_total = 0
nb_total_new = 0

# Loading files from previous loads to get their 001

f001previous = {}
for subdir, dirs, files in os.walk("SRC/PREVIOUS"):
	for f in sorted([fi for fi in files if fi.endswith("USM")], reverse=True):
		filename = os.path.join(subdir,f)
		reader = MARCReader(open("%s" % filename))
		
		for record in reader:
			f001 = record.get_fields("001")[0].data
			f001previous[f001] = f

print "Records loaded during previous loads: %s" % len(f001previous)

'''
This file will process the Dawsonera files for the following enhancements:
- Remove any 020 that is not for e-book
'''
f001done = {}
outputFilename = "TMP/global-step1.mrc"
out = open(outputFilename, 'wb');

files = [f for f in os.listdir('SRC')]
for f in files:
	filename = os.path.join("SRC",f)
	if os.path.isfile(filename):
		print "# # # # # # # # # # # #"
		print "Reading: %s" % filename
		reader = MARCReader(open("%s" % filename))

		nb = 0
		nb_new = 0
		for record in reader:
			f001 = record.get_fields("001")[0].data

			if f001 in f001previous:
				print "Skipping %s {previous load : %s}" % (f001, f001previous[f001])
				pass
			elif f001 in f001done:
				print "Skipping %s {current load}" % f001
				pass
			else:
				f001done[f001] = f001
				nb_isbn_ebook = 0
				nb += 1					
				for f010 in record.get_fields("010"):
					record.remove_field(f010)
				
				for f015 in record.get_fields("015"):
					record.remove_field(f015)
				
				for f016 in record.get_fields("016"):
					record.remove_field(f016)
				
				for f020 in record.get_fields("020"):
					isbn_ebook = ""
					f020_out = []
					for i in range(0, len(f020.subfields), 2): 
						code = f020.subfields[i]
						value = f020.subfields[i + 1]

						if "e-book" in value:
							nb_isbn_ebook += 1
							if isbn_ebook != "":
								print "###################################"
								print "###################################"
								print "######## ", isbn, " duplicated ########"
								print "###################################"
								print "###################################"
								exit()
							isbn_ebook = value
							f020_out.append("a")
							f020_out.append(value)
					
					if isbn_ebook == "":
						record.remove_field(f020)
					else:
						f020.subfields = f020_out
				
				# We check the 856 because at the moment they don't contain $z
				nb856 = 0
				for f856 in record.get_fields("856"):
					tab_z = f856.get_subfields("z")
					nb856 += 1
					if len(tab_z) == 0:
						f856.add_subfield("z", u"View eBook online.")
				
				if nb856 == 0:
					print "No 856 for this"
					exit()
				
				if len(record.get_fields("020")) == 0:
					print "Pas de 020 pour %s !" % f001
				elif nb_isbn_ebook == 0:
					print "020 but no e-book one for %s" % f001
				try:
					out.write(record.as_marc())
				except:
					record.set_force_utf8(True)
					try:
						out.write(record.as_marc())
					except:
						print "Unable to export %s" % record.get_fields("001")[0].data
						pass
				
		nb_total += nb

		print "%s records in file" % (nb)
out.close()


print "Total records: %s # Unique records: %s" % (nb_total, nb_total_new)
