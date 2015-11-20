#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib, re, json
from datetime import date
import sys
nb_total = 0
nb_total_new = 0
filename = "mergedFile.mrc"
reader = MARCReader(open("TMP/%s" % filename), force_utf8=True);

today =  date.today()

outfile = open("OUT/mergedFile-loading-ok-%s.mrc" % today, "w")
outfile_exception = open("OUT/mergedFile-manually-handle-%s.txt" % today, "w")


nb = 0
nb_new = 0
nb_keep = 0
for record in reader:
	nb += 1
	f001 = record.get_fields("001")[0].data
	isbn = str(record.get_fields("020")[0].value())
	isbn = isbn.replace(" (e-book) :", "")
	isbn = isbn.replace(" (e-book)", "")
	

	keepRecord = True
	
	if not re.match(r"^[\dX]+$", isbn):
		print record.get_fields("020")[0].value()
		print "Error with ISBN #%s# [%s]" % (isbn, f001)
		sys.exit()
	
	url = "http://capitadiscovery.co.uk/yorksj/items.json?query=isbn%3A" + isbn + "&target=catalogue"
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	# We can find at least page with this ISBN
	if len(data) > 0:
		bibid = ""
		hasUrl = False
		hasUrlFull = ""
		
		for a in data:
			if re.match(r"http:\/\/capitadiscovery\.co\.uk\/yorksj\/items\/(.*)$", a):
				url = a
				bibid = re.sub(r"http:\/\/capitadiscovery\.co\.uk\/yorksj\/items\/(.*)$", r"\1", url)
				# We are going to load the json of the record
				responseDetailed = urllib.urlopen(url + ".json")
				dataDetailed = json.loads(responseDetailed.read())
				for b in dataDetailed:
					if b == url:
						for c in dataDetailed[b]:
							if c == "http://purl.org/dc/terms/hasVersion":
								hasUrl = True
								if len(dataDetailed[b][c]) == 1:
									hasUrlFull = dataDetailed[b][c][0]["value"]
								else:
									print "TOO MUCH SIZE"
									exit()
		
		if hasUrl and bibid:
			if "vlebooks" in hasUrlFull:
				print "EXISTS with URL on vlebooks %s [%s], will be overwritten" % (f001, bibid)
			else:
				print "EXISTS with URL outside vlebooks %s [%s]" % (f001, bibid)
				print hasUrlFull
				exit()
	else:
		print "# NEW: %s - %s" % (isbn, record["245"].get_subfields("a")[0])
		keepRecord = False
		
	if keepRecord:
		nb_keep += 1
		outfile.write(record.as_marc())
	else:
		outfile_exception.write(str(record))
		outfile_exception.write("\n")


outfile.close()
print "Out of %s, %s will be updated" % (nb, nb_keep)
