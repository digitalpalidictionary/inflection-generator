#!/usr/bin/env python3.10
# coding: utf-8

import pandas as pd
from modules import clean_machine
import pickle
from timeis import timeis, tic, toc, white, green, yellow, line, red
import re

tic()
print(f"{timeis()} {line}")
print(f"{timeis()} {yellow}finding all missing words")
print(f"{timeis()} {line}")

def make_text_list():
	print(f"{timeis()} {green}making text list", end=" ")
	text_list = []
	text_path = "../Cst4/txt/"
	texts = []
	# texts += ["vin01m.mul.xml.txt"]  # VIN1
	# texts += ["vin02m1.mul.xml.txt"]  # VIN2
	# texts += ["vin02m2.mul.xml.txt"]  # VIN3
	# texts += ["vin02m3.mul.xml.txt"]  # VIN4
	# texts += ["vin02m4.mul.xml.txt"]  # VIN5

	# texts = ["s0101m.mul.xml.txt"]  # DN1
	# texts += ["s0102m.mul.xml.txt"]  # DN2
	# texts += ["s0103m.mul.xml.txt"]  # DN3

	# texts += ["s0201m.mul.xml.txt"]  # MN1
	# texts = ["s0202m.mul.xml.txt"]  # MN2
	# texts = ["s0203m.mul.xml.txt"]  # MN3

	# texts = ["s0301m.mul.xml.txt"]  # SN1
	# texts = ["s0302m.mul.xml.txt"]  # SN2
	# texts = ["s0303m.mul.xml.txt"]  # SN3
	texts = ["s0304m.mul.xml.txt"]  # SN4
	# texts = ["s0305m.mul.xml.txt"]  # SN5

	# texts += ["s0401m.mul.xml.txt"]  # AN1 mūla
	# texts += ["s0402m1.mul.xml.txt"]  # AN2 mūla
	# texts += ["s0402m2.mul.xml.txt"]  # AN3 mūla
	# texts += ["s0402m3.mul.xml.txt"]  # AN4 mūla
	# texts += ["s0403m1.mul.xml.txt"]  # AN5 mūla
	# texts += ["s0403m2.mul.xml.txt"]  # AN6 mūla
	# texts += ["s0403m3.mul.xml.txt"]  # AN7 mūla
	# texts += ["s0404m1.mul.xml.txt"]  # AN8 mūla
	# texts += ["s0404m2.mul.xml.txt"]  # AN9 mūla
	# texts += ["s0404m3.mul.xml.txt"]  # AN10 mūla
	# texts += ["s0404m4.mul.xml.txt"]  # AN11 mūla

	for text in texts:
		with open (f"{text_path}{text}", "r") as f:
			text_read = f.read()
		clean_text = clean_machine(text_read)
		text_list += clean_text.split()
	
	print(f"{white}{len(text_list)}")
	return text_list


text_list = make_text_list()

def make_sc_text_list():
	print(f"{timeis()} {green}making sutta central text list", end=" ")
	sc_text_list = []
	sc_path = "../Tipitaka-Pali-Projector/tipitaka_projector_data/pali/"
	
	sc_texts = []
	# sc_texts += ["11010a.js"]  # VIN1
	# sc_texts += ["11020a.js"]  # VIN2
	# sc_texts += ["11030a.js"]  # VIN3
	# sc_texts += ["11040a.js"]  # VIN4
	# sc_texts += ["11050a.js"]  # VIN5

	# sc_texts += ["21010a.js"]  # DN1
	# sc_texts += ["21020a.js"]  # DN2
	# sc_texts += ["21030a.js"]  # DN3

	# sc_texts += ["31010a.js"]  # MN1
	# sc_texts += ["31020a.js"]  # MN2
	# sc_texts += ["31030a.js"]  # MN3

	# sc_texts += ["41010a.js"]  # SN1
	# sc_texts += ["41020a.js"]  # SN2
	# sc_texts += ["41030a.js"]  # SN3
	sc_texts += ["41040a.js"]  # SN4
	# sc_texts += ["41050a.js"]  # SN5

	# sc_texts += ["51010a.js"]  # AN1
	# sc_texts += ["51020a.js"]  # AN2
	# sc_texts += ["51030a.js"]  # AN3
	# sc_texts += ["51040a.js"]  # AN4
	# sc_texts += ["51050a.js"]  # AN5
	# sc_texts += ["51060a.js"]  # AN6
	# sc_texts += ["51070a.js"]  # AN7
	# sc_texts += ["51080a.js"]  # AN8
	# sc_texts += ["51090a.js"]  # AN9
	# sc_texts += ["51100a.js"]  # AN10
	# sc_texts += ["51110a.js"]  # AN11

	# sc_texts += ["61080a.js"]  # TH
	# sc_texts += ["61090a.js"]  # THI

	for sc_text in sc_texts:
		with open(f"{sc_path}{sc_text}", "r") as f:
			text_read = f.read()
		text_read = re.sub("var P_HTM.+", "", text_read)
		text_read = re.sub("""P_HTM\\[\\d+\\]="\\*""", "", text_read)
		text_read = re.sub("""\\*\\*.+;""", "", text_read)
		text_read = re.sub("\n", " ", text_read)
		text_read = text_read.lower()
		clean_text = clean_machine(text_read)
		sc_text_list += clean_text.split()

	# print(sc_text_list)
	print(f"{white}{len(sc_text_list)}")
	return sc_text_list


sc_text_list = make_sc_text_list()


def make_sp_mistakes_list():
	print(f"{timeis()} {green}making spelling mistakes list", end=" ")
	sp_mistakes = pd.read_csv("../inflection generator/sandhi/spelling mistakes.csv", sep="\t", dtype=str, header=None)
	sp_mistakes_list = sp_mistakes[0].to_list()
	print(f"{white}{len(sp_mistakes_list)}")
	return sp_mistakes_list

sp_mistakes_list = make_sp_mistakes_list()

def make_variant_reading_list():
	print(f"{timeis()} {green}making variant reading list", end=" ")
	var_df = pd.read_csv("../inflection generator/sandhi/variant readings.csv", sep="\t", dtype=str, header=None)
	var_list = var_df[0].to_list()
	print(f"{white}{len(var_list)}")
	return var_list

var_list = make_variant_reading_list()

def make_sandhi_list():
	print(f"{timeis()} {green}making sandhi list", end=" ")
	sandhi_df = pd.read_csv("allwords/sandhi.csv", sep="\t", dtype=str, header=None)
	sandhi_list = sandhi_df[0].to_list()
	print(f"{white}{len(sandhi_list)}")
	return sandhi_list

sandhi_list = make_sandhi_list()

text_list = text_list + sc_text_list
text_set = set(text_list) - set(sandhi_list)
text_set = text_set - set(sp_mistakes_list)
text_set = text_set - set(var_list)
text_list = sorted(text_set, key=text_list.index)

def make_all_inflections_no_meaning_set():
	print(f"{timeis()} {green}making all inflections with no meaning set", end=" ")
	with open("output/all inflections dict", "rb") as p:
		all_infl_dict = pickle.load(p)

	all_inflections_no_meaning = []
	for word in all_infl_dict:
		if all_infl_dict[word]["meaning"] == "":
		# if all_infl_dict[word]["sutta1"] == False:
			if all_infl_dict[word]["pos"] != "sandhix":
				all_inflections_no_meaning += all_infl_dict[word]["inflections"]
	
	all_inflections_no_meaning_set = set(all_inflections_no_meaning)
	print(f"{white}{len(all_inflections_no_meaning_set)}")
	return all_inflections_no_meaning_set


all_inflections_no_meaning_set = make_all_inflections_no_meaning_set()


def write_all_missing_words():
	print(f"{timeis()} {green}writing all missing words", end=" ")
	counter=0
	with open("output/allwords/missing meanings.csv", "w") as f:
		for word in text_list:
			if word in all_inflections_no_meaning_set:
				f.write(f"{word}\n")
				counter+=1
		f.write(f"{counter}\n")
	print(f"{white}{counter}")
	

write_all_missing_words()
toc()


