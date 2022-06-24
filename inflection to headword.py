#!/usr/bin/env python3.10
#coding: utf-8

import pickle
import json
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
print(f"{timeis()} {green}generating all inflections to headwords dict")

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

print(f"{timeis()} {green}total\t{white}{len(inflection_to_headword)}")
print(f"{timeis()} {green}sorting headwords")
for inflection in inflection_to_headword:
	inflection_to_headword[inflection]["headwords"] = sorted(inflection_to_headword[inflection]["headwords"])


print(f"{timeis()} {green}saving to picle csv and json")
with open("output/inflection to headwords dict", "wb") as f:
	pickle.dump(inflection_to_headword, f)
df = pd.DataFrame.from_dict(inflection_to_headword, orient='index')
df.rename_axis("inflection", inplace=True)
df.to_csv("output/inflection to headwords dict.csv", sep="\t")
df.to_json("output/inflection to headwords dict.json", force_ascii=False, orient="index", indent=6)

toc()
