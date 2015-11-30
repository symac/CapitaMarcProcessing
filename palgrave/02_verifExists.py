#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib, re, json, sys
import datetime
today = datetime.date.today()

nb_total = 0
nb_total_new = 0
filename = "SOCIALSCIENCES2015-auth"
reader = MARCReader(open("OUT/%s.mrc" % filename))

outfile = open("OUT/%s-ok-import.mrc" % filename, "w")
outfile_exception = open("OUT/%s-manually-handle.mrc" % filename, "w")

def writeRecord(record, fh):
	try:
		fh.write(record.as_marc())
	except:
		record.set_force_utf8(True)
		try:
			fh.write(record.as_marc())
		except:
			e = sys.exc_info()[0]
			print "Unable to export %s" % record.get_fields("001")[0].data
			print e
			exit()
			pass

nb = 0
nb_new = 0
nb_keep = 0
for record in reader:
	nb += 1
	if nb > 5000:
		exit()
	else:
		keepRecord = True
		noIsbn = False
		f001 = record.get_fields("001")[0].data
		
		if len(record.get_fields("020")) > 0:
			isbn = str(record.get_fields("020")[0].get_subfields("a")[0]).replace(" (e-book)", "")
			isbn = isbn.replace(" :", "")
			isbn = isbn.upper()
			
			if not re.match(r"^[\dXx]+$", isbn):
				for f020 in record.get_fields("020"):
					print f020.value().encode("utf-8")
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
										# Already there, we won't keep it
										keepRecord = False
									
										for v in dataDetailed[b][c]:
											url = v["value"]
											if "palgrave" in url:
												print "EXISTS with URL on palgrave %s [%s]" % (f001, bibid)
											else:
												print "EXISTS with URL outside palgrave %s [%s]" % (f001, bibid)
			else:
				print "# NEW: %s - %s" % (isbn, record["245"].get_subfields("a")[0])
				keepRecord = True
		else:
			# No ISBN, how will this match?
			keepRecord = False
			noIsbn = True

		
		if keepRecord:
			nb_keep += 1
			writeRecord(record, outfile)
		else:
			if noIsbn:
				writeRecord(record, outfile_exception_noisbn)
			else:
				writeRecord(record, outfile_exception)


outfile.close()
print "Out of %s, %s will be updated" % (nb, nb_keep)
