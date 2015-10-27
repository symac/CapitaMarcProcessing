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

fh = open('SJMISSNRTD-records.mrc', 'rb')
reader = ExceptionHandlingIterator(MARCReader(fh, force_utf8=True, utf8_handling='ignore', to_unicode=True))

nb = 0
for record in reader:
	nb += 1

	for f in record.get_fields("998"):
		barcode = f.get_subfields('i')[0]
		tab = f.get_subfields('l')
		for v in tab:
			if str(v) == "SJMISSNRTD":
				
				year = f.get_subfields('d')[0].split("/")[2]
				month = f.get_subfields('d')[0].split("/")[1]
				if len(month) == 1:
					month = "0" + month
				
				compar = year + month
				
				if int(compar) < 201208:
					print "%s [%s]" % (barcode, compar)
