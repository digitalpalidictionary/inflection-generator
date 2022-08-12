#!/usr/bin/env python3.10
# coding: utf-8

import pandas as pd
from modules import clean_machine
import pickle
from timeis import timeis, tic, toc, white, green, yellow, line, red

tic()
print(f"{timeis()} {line}")
print(f"{timeis()} {yellow}finding all missing words")
print(f"{timeis()} {line}")

def make_text_list():
	print(f"{timeis()} {green}making text list", end=" ")
	text_list = []
	text_path = "../Cst4/txt/"
	# texts = ["s0101m.mul.xml.txt"]
	# texts += ["s0102m.mul.xml.txt"]
	# texts += ["s0103m.mul.xml.txt"]
	# texts += ["s0201m.mul.xml.txt"]
	# texts = ["s0202m.mul.xml.txt"]
	texts = ["s0203m.mul.xml.txt"]
	# texts = ["s0502a.att.xml.txt"]
	for text in texts:
		with open (f"{text_path}{text}", "r") as f:
			text_read = f.read()
		clean_text = clean_machine(text_read)
		text_list += clean_text.split()
	
	print(f"{white}{len(text_list)}")
	return text_list

text_list = make_text_list()

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

text_set = set(text_list) - set(sandhi_list)
text_set = text_set - set(sp_mistakes_list)
text_set = text_set - set(var_list)
text_list = sorted(text_set, key=text_list.index)

def make_all_inflections_set():
	print(f"{timeis()} {green}making all inflections set", end=" ")
	with open("output/all inflections dict", "rb") as p:
		all_infl_dict = pickle.load(p)

	all_inflections = []
	for word in all_infl_dict:
		all_inflections += all_infl_dict[word]["inflections"]
	
	all_inflections_set = set(all_inflections)
	print(f"{white}{len(all_inflections_set)}")
	return all_inflections_set

all_inflections_set = make_all_inflections_set()

def write_all_missing_words():
	print(f"{timeis()} {green}writing all missing words", end=" ")
	counter=0
	with open("output/allwords/missing words.csv", "w") as f:
		for word in text_list:
			if word not in all_inflections_set:
				f.write(f"{word}\n")
				counter+=1
	print(f"{white}{counter}")

write_all_missing_words()
toc()