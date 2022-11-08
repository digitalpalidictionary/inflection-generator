#!/usr/bin/env python3.10
# coding: utf-8

import pickle
import json
import re
import pandas as pd

from timeis import timeis, yellow, line, white, green, red, tic, toc
from modules import export_changed_inflections_to_json, transliterate_aksharamukha, transliterate_path_nirvana, import_path_nirvana_transliterations

tic()
print(f"{timeis()} {yellow}transliterating changed headwords and sandhis")
print(f"{timeis()} {line}")

with open ("output/changed headwords", "rb") as f:
	changed_headwords = pickle.load(f)
	print(f"{timeis()} {green}changed headwords size {white}{len(changed_headwords)}")

with open ("output/all inflections dict", "rb") as f:
	all_inflections_dict = pickle.load(f)
	print(f"{timeis()} {green}all inflections dict size {white}{len(all_inflections_dict)}")

with open("output/sandhi dict", "rb") as f:
	sandhi_dict = pickle.load(f)
	print(f"{timeis()} {green}sandhi dict size {white}{len(sandhi_dict)}")

# add all sandhis to all inflections dict
print(f"{timeis()} {green}adding sandhis to all inflectios dict", end=" ")
added_sandhi=[]

for sandhi in sandhi_dict:
	if sandhi not in all_inflections_dict:
		all_inflections_dict[sandhi] = {
			"pos": "sandhix", 
			"meaning":"", 
			"meaning2":"", 
			"stem":"!", 
			"pattern":"", 
			"inflections":{sandhi}, 
			"sinhala":{}, 
			"devanagari":{}, 
			"thai":{}, 
			"sutta1":False, 
			"sutta2":False
		}
		added_sandhi += [sandhi]

print(f"{white}{len(added_sandhi)}")


# delete unused sandhis
print(f"{timeis()} {green}deleting unused sandhis", end=" ")

del_counter = 0
for headword in list(all_inflections_dict):
	if all_inflections_dict[headword]['pos'] == "sandhix":
		if headword not in sandhi_dict:
			all_inflections_dict.pop(headword)
			del_counter += 1

print(f"{white}{del_counter}")


# export all the changed headwords to json for path nirvana node script
print(f"{timeis()} {green}exporting changed headwords to json", end= " ")

export_changed_inflections_to_json (
	all_inflections_dict,
	changed_headwords,
	added_sandhi
)

print(f"{white}{len(changed_headwords) + len(added_sandhi)}")

# send to transliterate aksharamukha
print(f"{timeis()} {green}transliterating with aksharamukha", end=" ")

all_inflections_dict = transliterate_aksharamukha (
	all_inflections_dict,
	changed_headwords,
	added_sandhi
)

print(f"{white}ok")

# send to transliterate path nirvana in node.js
print(f"{timeis()} {green}transliterating with path nirvana in node.js", end=" ")
transliterate_path_nirvana()
all_inflections_dict = import_path_nirvana_transliterations (
	all_inflections_dict
)

print(f"{timeis()} {green}pickling all inflections dict", end=" ")
with open("output/all inflections dict", "wb") as f:
	pickle.dump(all_inflections_dict, f)
print(f"{white}{len(all_inflections_dict)}")

toc()

