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

outfile_ok = open("OUT/mergedFile-loading-ok-%s.mrc" % today, "w")
outfile_exception = open("OUT/mergedFile-manually-handle-%s.mrc" % today, "w")
logfile = open("OUT/mergedFile-log-%s.txt" % today, "w")

referenceId = ""

def searchIsbn(isbn, printIsbn = False):
	global referenceId
	isbnBase = isbn
	isbn = isbn.replace(" (e-book) :", "")
	isbn = isbn.replace(" (electronic bk.)", "")
	isbn = isbn.replace(" electronic bk.", "")
	isbn = isbn.replace(" (e-book)", "")
	isbn = re.sub(r" \(ebook\).*", "", isbn)
	
	if printIsbn:
		isbn = re.sub(r"^Print version :? ?", "", isbn)
		
	
	print "\t\t\t%s" % isbn
	
	keepRecord = 1 # Par defaut, on garde la notice
	
	if not re.match(r"^[\dX]+$", isbn):
		print "Error with ISBN #%s# => %s [%s]" % (isbnBase, isbn, f001)
		sys.exit()
	
	if printIsbn == False:
		url = "http://capitadiscovery.co.uk/yorksj/items.json?query=isbn%3A" + isbn + "&target=catalogue"
	else:
		url = "http://capitadiscovery.co.uk/yorksj/items.json?query=" + isbn + "&target=catalogue"
	# url = "http://capitadiscovery.co.uk/yorksj/items.json?facet%5B0%5D=format%3A%22ebook%22&query=isbn%3A" + isbn + "&adv=t"
	response = urllib.urlopen(url)
	content = response.read()
	try:
		data = json.loads(content)
	except:
		print f001 + " - " + isbn + " # UNABLE TO READ (no result) %s" % isbn
		data = [];

	#print "Searching %s" % url
	# We can find at least page with this ISBN
	if len(data) > 0:
		bibid = ""
		hasUrl = False
		hasUrlFull = ""
		
		for a in data:
			if re.match(r"http:\/\/capitadiscovery\.co\.uk\/yorksj\/items\/(.*)$", a):
				url = a
				bibid = re.sub(r"http:\/\/capitadiscovery\.co\.uk\/yorksj\/items\/(.*)$", r"\1", url)
				referenceId = bibid
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
			if "oxford" in hasUrlFull:
				print "\t" + f001 + " - " + isbn + " - EXISTS with URL on oxford %s [%s], will be excluded based on electronic ISBN" % (f001, bibid)
				keepRecord = 0
			else:
				print "\t" + f001 + " - " + isbn + " - EXISTS with URL outside ebscohost %s [%s]" % (f001, bibid)
				keepRecord = 0
				sys.exit()
	else:
		# We have not found it, yet
		keepRecord = -1 # Nothing found, we might need to double check
	#print "\t\tKEEP: %s" % keepRecord
	return keepRecord
nb = 0
nb_new = 0
nb_keep = 0
for record in reader:
	nb += 1
	if nb < 0:
		pass
	else:
		f001 = record.get_fields("001")[0].data
		print "## %s ##" % f001
		counter = 0
		keepRecord = -1
		isbn = ""
		
		while counter < len(record.get_fields("020")) and keepRecord == -1:
			isbn = str(record.get_fields("020")[counter].value())
			keepRecord = searchIsbn(isbn)
			counter += 1
		
		# When we are there we have checked all the electronic ISBN, we now need to check the print one in case
		counter = 0
		while counter < len(record.get_fields("776")) and keepRecord == -1:
			print_isbn = str(record.get_fields("776")[counter].value())
			keepRecord = searchIsbn(print_isbn, True)
			#print "Print → %s" % keepRecord
			counter += 1
		
		operation = ""
		if keepRecord == 1:
			nb_keep += 1
			operation = "UPDATE\t%s" % referenceId
			outfile_ok.write(record.as_marc())
		elif keepRecord == 0:
			outfile_exception.write(record.as_marc())
			operation = "EXISTS\t%s" % referenceId
		elif keepRecord == -1:
			nb_keep += 1
			outfile_ok.write(record.as_marc())
			operation = "CREATE"
		else:
			print "NOthing to do for %s" % keepRecord
			sys.exit()
		
		logfile.write("%s\t%s\t%s\n" % (f001, isbn, operation))

outfile_ok.close()
outfile_exception.close()

print "Out of %s, %s will be updated" % (nb, nb_keep)
