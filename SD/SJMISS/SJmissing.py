#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode

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

fh = open('final-sd.mrc', 'rb')
reader = ExceptionHandlingIterator(MARCReader(fh, force_utf8=True, utf8_handling='ignore', to_unicode=True))

fout = open('SJMISSNRTD-records.mrc', 'wb')

listeId = {}
duplicateId = []
nb = 0
for record in reader:
	nb += 1
	if not nb % 5000:
		print nb
	keep = 0
	for f in record.get_fields("998"):
		barcode = f.get_subfields('i')[0]
		tab = f.get_subfields('l')
		for v in tab:
			if str(v) == "SJMISSNRTD":
				print "%s" % (barcode)
				keep = 1
	
	if keep == 1:
		fout.write(record.as_marc())