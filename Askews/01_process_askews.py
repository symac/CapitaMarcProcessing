#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib
from os import listdir
from os.path import isfile, join
import sys

nb_total = 0
nb_total_new = 0

loadedPreviously = []
# We are loading data that have already been processed to prevent any udplicate
for subdir, dirs, files in os.walk("SRC_DONE"):
	for f in sorted([fi for fi in files if fi.endswith(".mrc")], reverse=True):
		filename = os.path.join(subdir,f)
		reader = MARCReader(open("%s" % filename), force_utf8=True);
		for record in reader:
			f001 = record.get_fields("001")[0].data
			loadedPreviously.append(f001)


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
	for f in sorted([fi for fi in files if fi.endswith(".mrc")], reverse=True):
		print f
		filename = os.path.join(subdir,f)
		print "# # # # # # # # # # # #"
		print "Reading: %s" % filename

		reader = MARCReader(open("%s" % filename), force_utf8=True);
		
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
			elif f001 in loadedPreviously:
				print "Already loaded previously, skipping [%s - %s]" % (f001, record.get_fields("020")[0].get_subfields("a"))
			else:
				nb_new += 1
				f001done[f001] = f
				for f020 in record.get_fields("020"):
					isbn_ebook = ""
					f020_out = []
					for i in range(0, len(f020.subfields), 2): 
						code = f020.subfields[i]
						value = f020.subfields[i + 1]

						if "e-book" in value:
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
				if len(record.get_fields("020")) == 0:
					print "Pls de 020!!!!"
					exit()
				out.write(record.as_marc())
		
		nb_total += nb
		nb_total_new += nb_new
		print "%s records in file [%s new]" % (nb, nb_new)
		out.close()

print "Total records: %s # Unique records: %s" % (nb_total, nb_total_new)
os.chdir("TMP")
os.system("mergeFiles.py -o mergedFile.mrc")