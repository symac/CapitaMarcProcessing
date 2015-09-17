#!usr/bin/env python
# -*- coding: utf-8 -*-
from pymarc import MARCReader, marc8_to_unicode
import os, urllib

nb_total = 0
nb_total_new = 0

loadedWorkFlows = ["AH3700303", "AH3710631", "AH3710728", "AH20665025", "AH23067117", "AH23067118", "AH24068677", "AH24069505", "AH24547580", "AH24925817", "AH25157368", "AH25524916", "AH25866395", "AH26788309", "AH27080542", "AH25858700", "AH26183745", "AH26317829", "AH26385947", "AH27080908", "AH27254759", "AH28053618", "AH28303348", "AH28314975", "AH28401801", "AH12604407", "AH15188816", "AH24247707", "AH24925566", "AH24925567", "AH25718965", "AH26317934", "AH27088246", "AH27095748", "AH25898035", "AH26129902", "AH3714799", "AH3925628", "AH19771129", "AH20295696", "AH23958080", "AH24093638", "AH24925458", "AH25735512", "AH26311787", "AH27236109", "AH27521643", "AH28520541", "AH28621593", "AH3906521", "AH4263628", "AH4284479", "AH4285155", "AH13346184", "AH13351026", "AH13353244", "AH13356766", "AH13383754", "AH20280038", "AH20725630", "AH20848227", "AH21514821", "AH21619408", "AH21624331", "AH21626909", "AH21639770", "AH21641044", "AH22923073", "BDZ0022174723", "AH23051286", "AH23051983", "AH23052927", "AH23053129", "AH23057008", "AH23064514", "AH23068022", "AH23093696", "AH24082039", "AH24219862", "AH24220824", "AH24392549", "AH24527852", "AH24606114", "AH24670586", "AH24671765", "AH24925637", "AH24960565", "AH24973981", "AH25002003", "AH25005559", "AH25005671", "AH25006418", "AH25034486", "AH25045634", "AH25046857", "AH25154539", "AH25156650", "AH25157630", "AH25159728", "AH25228812", "AH25459913", "AH25461193", "AH25541497", "AH25541900", "AH25719679", "AH25858155", "AH25954853", "AH25960641", "AH26068645", "AH26088733", "AH26151782", "AH26152381", "AH26183238", "AH26310996", "AH26318018", "AH26318347", "AH26321634", "AH26322023", "AH26344687", "AH26381060", "AH26466614", "AH26781500", "AH26817010", "AH26817493", "AH27257282", "AH28111697", "AH28251286", "BDZ0025266333", "AH3715007", "AH3719515", "AH3919580", "AH3925097", "AH4284341", "AH4284594", "AH13384771", "AH21624009", "BDZ0022893884", "AH23052750", "AH23056533", "AH23093912", "AH23958268", "AH23958549", "AH23958592", "AH24071472", "AH24072833", "AH24088372", "AH24426048", "AH24461109", "AH24925482", "AH24974135", "AH24974364", "AH25003809", "AH25069334", "AH25461305", "AH25461434", "AH25461466", "AH25960666", "AH27078984", "AH27256124", "AH3906931", "AH22921094", "AH23083816", "AH25157025", "AH25564309", "AH20725597", "AH25037120", "AH27078984", "AH26859594", "AH13352028", "AH23052841", "AH23081939", "AH25006441", "AH26300842", "AH25461220", "AH25564303", "AH25702602", "AH25702628", "AH25858171", "AH26152216", "AH26203383", "AH26394480", "AH26967808", "AH27080978", "AH27080981", "AH27081049", "AH27081108", "AH27081180", "AH27081414", "AH27081676", "AH27088189", "AH27095816", "AH27095821", "AH27183819", "AH27203450", "AH27207377", "AH28068053", "AH28301232", "AH28301314", "AH13351574", "AH23051195", "AH23958026", "AH23958448", "AH24925122", "AH25003590", "AH25461332", "AH25702976", "AH26860814", "AH27203450", "AH27206825", "AH23050979", "AH3923874", "AH23958709", "AH25574848", "AH24068677", "AH26183582", "AH26412695", "AH27256953", "AH3715288", "AH23958710", "AH24081220", "AH25156842", "AH25387349", "AH25461175", "AH27207516", "AH3711694", "AH23067188", "AH24069396", "AH24072589", "AH24088149", "AH24100584", "AH24394055", "AH26154251", "AH26831695", "AH27274791", "AH26412695", "AH24220381", "AH25743214", "AH25821458", "AH26813281", "AH26887465", "AH3700971", "AH3701551", "AH3701829", "AH3702473", "AH3710489", "AH3714244", "AH3716262", "AH3717425", "AH3717584", "AH3718650", "AH3906720", "AH3919735", "AH3920228", "AH3921699", "AH4264073", "AH12951520", "AH15187191", "AH15188906", "AH20270444", "AH20277141", "AH21631815", "AH21635969", "AH23069485", "AH23091093", "AH23095301", "AH23958377", "AH23958491", "AH23958526", "AH23958624", "AH24038157", "AH24068166", "AH24068491", "AH24069115", "AH24069234", "AH24069325", "BDZ0020784543", "AH24080309", "AH24087052", "AH24425981", "AH25201860", "AH25270642", "AH25270659", "AH25270694", "AH25270768", "AH25270871", "AH25270882", "AH25270896", "AH25470691", "AH25701521", "AH25737257", "AH25843187", "AH26030214", "AH26085197", "AH26088226", "AH26183582", "AH26311334", "AH26458521", "AH26817300", "AH26827196", "AH26827233", "AH26857804"]

'''
This file will process the askews files to remove any 020 that is not for an ebook
'''
f001done = {}
for subdir, dirs, files in os.walk("SRC"):
	for f in sorted([fi for fi in files if fi.endswith(".mrc")], reverse=True):
		filename = os.path.join(subdir,f)
		print "# # # # # # # # # # # #"
		print "Reading: %s" % filename

		reader = MARCReader(open("%s" % filename), force_utf8=True);
		
		outputFilename = "OUT/%s-clean.mrc" % os.path.splitext(f)[0]
		out = open(outputFilename, 'wb');
		nb = 0
		nb_new = 0
		for record in reader:
			nb += 1
			f001 = record.get_fields("001")[0].data
			if f001 in f001done:
				# print "Skipping %s, already done in %s" % (f001, f001done[f001])
				pass
			elif f001 in loadedWorkFlows:
				print "Already loaded in WorkFlows, skipping [%s - %s]" % (f001, record.get_fields("020")[0].get_subfields("a"))
				print record.get_fields("856")[0].get_subfields("u")
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
os.chdir("OUT")
os.system("mergeFiles.py -o ../mergedFile.mrc")
