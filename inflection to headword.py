#!/usr/bin/env python3.10
#coding: utf-8

import pickle
import json
import re
import pandas as pd
from timeis import timeis, green, white, yellow, line, tic, toc

tic()

with open("output/all inflections dict", "rb") as f:
	all_inflections_dict = pickle.load(f)

inflection_to_headword = {}
counter = 0
length = len(all_inflections_dict)

print(f"{timeis()} {yellow}all inflection to headwords dict")
print(f"{timeis()} {line}")
print(f"{timeis()} {green}generating all inflection to headwords dict")

# make lists of all_headwords & clean version
all_headwords = list(all_inflections_dict.keys())
all_headwords_clean = set()

for headword in all_inflections_dict:
	all_headwords_clean.add(re.sub(" \\d*$", "", headword))

# add all inflections
for headword in all_inflections_dict:
	if counter % 5000 == 0:
		print(f"{timeis()} {white}{counter}/{length}\t{headword} ")

	inflections = all_inflections_dict[headword]["inflections"]
	for inflection in inflections:
		if inflection not in inflection_to_headword.keys():
			inflection_to_headword.update({inflection: {"headwords":set()}})
			inflection_to_headword[inflection]["headwords"].add(headword)
		else:
			inflection_to_headword[inflection]["headwords"].add(headword)
	counter+=1


# add all roots
print(f"{timeis()} {green}adding roots")
roots_df = pd.read_csv("../csvs/roots.csv", sep="\t")
roots_df.fillna("", inplace=True)

filter = roots_df["Count"] != 0
roots_df = roots_df[filter]
roots_list = []
roots_list = roots_df["Root"].to_list()
counter = 0

for root in roots_list:
	if counter % 100 == 0:
		print(f"{timeis()} {white}{counter}/{len(roots_list)}\t{root}")

	root_clean = re.sub(" \\d*$", "", root)
	root_no_sign = root_clean.replace("√", "")

	# add roots themselves
	if root_clean not in inflection_to_headword.keys():
		inflection_to_headword.update({root_clean: {"headwords": set()}})
		inflection_to_headword[root_clean]["headwords"].add(root)
	else:
		inflection_to_headword[root_clean]["headwords"].add(root)

	# add root_no_sign
	if root_no_sign not in inflection_to_headword.keys():
		inflection_to_headword.update({root_no_sign: {"headwords": set()}})
		inflection_to_headword[root_no_sign]["headwords"].add(root)
	else:
		inflection_to_headword[root_no_sign]["headwords"].add(root)
	
	counter += 1


print(f"{timeis()} {green}total\t{white}{len(inflection_to_headword)}")
print(f"{timeis()} {green}sorting headwords")
for inflection in inflection_to_headword:
	inflection_to_headword[inflection]["headwords"] = sorted(inflection_to_headword[inflection]["headwords"])

print(f"{timeis()} {green}saving to picle csv and json")
with open("output/inflection to headwords dict", "wb") as f:
	pickle.dump(inflection_to_headword, f)

inflection_to_headword_json = json.dumps(
	inflection_to_headword, ensure_ascii=False, indent=4)
with open("../dpd-app/data/inflection to headwords dict.json", "w") as f:
    f.write(inflection_to_headword_json)

df = pd.DataFrame.from_dict(inflection_to_headword, orient='index')
df.rename_axis("inflection", inplace=True)
df.to_csv("output/inflection to headwords dict.tsv", sep="\t")

toc()
