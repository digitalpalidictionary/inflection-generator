#!/usr/bin/env python3.10
#coding: utf-8

import os
import pandas as pd
import sys
import warnings
import random
import json
import pickle
import re

from modules import clean_machine
from timeis import timeis, blue, green, yellow, line, white, red, tic, toc
from pathlib import Path
from difflib import SequenceMatcher
from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry

warnings.filterwarnings("ignore", category=FutureWarning)


print(f"{timeis()} {yellow}sandhi splitter")
print(f"{timeis()} {line}")

vowels = ["a", "ā", "i", "ī", "u", "ū", "o", "e"]


def make_text_set():

	print(f"{timeis()} {green}making text set", end = " ")
	text_list = []

	text_list += ["vin01m.mul.xml.txt"]  # VIN1 mūla
	text_list += ["vin02m1.mul.xml.txt"]  # VIN2 mūla
	# text_list += ["vin02m2.mul.xml.txt"]  # VIN3 mūla
	# text_list += ["vin02m3.mul.xml.txt"]  # VIN4 mūla
	# text_list += ["vin02m4.mul.xml.txt"]  # VIN5 mūla

	text_list += ["s0101m.mul.xml.txt"] # DN1 mūla
	text_list += ["s0102m.mul.xml.txt"] # DN2 mūla
	text_list += ["s0103m.mul.xml.txt"]  # DN3 mūla

	text_list += ["s0201m.mul.xml.txt"]  # MN1 mūla
	text_list += ["s0202m.mul.xml.txt"]  # MN2 mūla
	text_list += ["s0203m.mul.xml.txt"]  # MN3 mūla

	text_list += ["s0301m.mul.xml.txt"]  # SN1 mūla
	# text_list += ["s0302m.mul.xml.txt"]  # SN2 mūla
	# text_list += ["s0303m.mul.xml.txt"]  # SN3 mūla
	# text_list += ["s0304m.mul.xml.txt"]  # SN4 mūla
	# text_list += ["s0305m.mul.xml.txt"]  # SN5 mūla

	# text_list += ["s0401m.mul.xml.txt"]  # AN1 mūla
	# text_list += ["s0402m1.mul.xml.txt"]  # AN2 mūla
	# text_list += ["s0402m2.mul.xml.txt"]  # AN3 mūla
	# text_list += ["s0402m3.mul.xml.txt"]  # AN4 mūla
	# text_list += ["s0403m1.mul.xml.txt"]  # AN5 mūla
	# text_list += ["s0403m2.mul.xml.txt"]  # AN6 mūla
	# text_list += ["s0403m3.mul.xml.txt"]  # AN7 mūla
	# text_list += ["s0404m1.mul.xml.txt"]  # AN8 mūla
	# text_list += ["s0404m2.mul.xml.txt"]  # AN9 mūla
	# text_list += ["s0404m3.mul.xml.txt"]  # AN10 mūla
	# text_list += ["s0404m4.mul.xml.txt"]  # AN11 mūla

	text_list += ["s0202a.att.xml.txt"]  # MN2 aṭṭhakathā

	text_path = "../Cst4/txt/"
	text_string = ""
	
	for text in text_list:
		with open(f"{text_path}/{text}", "r") as f:
			text_string += f.read()

	text_string = clean_machine(text_string)
	text_set = set(text_string.split())

	with open(f"output/set text", "wb") as p:
		pickle.dump(text_set, p)
	
	print(f"{white} {len(text_set)}")


def make_sc_text_set():

	print(f"{timeis()} {green}making sutta central text set", end=" ")

	sc_path = "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/pali/"

	sc_texts = []
	sc_texts += ["11010a.js"]  # VIN1
	sc_texts += ["11020a.js"]  # VIN2
	# sc_texts += ["11030a.js"]  # VIN3
	# sc_texts += ["11040a.js"]  # VIN4
	# sc_texts += ["11050a.js"]  # VIN5

	sc_texts += ["21010a.js"]  # DN1
	sc_texts += ["21020a.js"]  # DN2
	sc_texts += ["21030a.js"]  # DN3

	sc_texts += ["31010a.js"]  # MN1
	sc_texts += ["31020a.js"]  # MN2
	sc_texts += ["31030a.js"]  # MN3

	sc_texts += ["41010a.js"]  # SN1
	# sc_texts += ["41020a.js"]  # SN2
	# sc_texts += ["41030a.js"]  # SN3
	# sc_texts += ["41040a.js"]  # SN4
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

	text_string = ""

	for sc_text in sc_texts:
		with open(f"{sc_path}/{sc_text}", "r") as f:
			text_string += f.read()

	text_string = re.sub("var P_HTM.+", "", text_string)
	text_string = re.sub("""P_HTM\\[\\d+\\]="\\*""", "", text_string)
	text_string = re.sub("""\\*\\*.+;""", "", text_string)
	text_string = text_string.lower()
	text_string = clean_machine(text_string)
	sc_text_set = set(text_string.split())

	with open("output/sc_text_set.csv", "w") as f:
		for word in sorted(sc_text_set):
			f.write(f"{word}\n")
			
	print(f"{white} {len(sc_text_set)}")
	return sc_text_set


def make_spelling_mistakes_set():
	global spelling_mistakes_set
	global spelling_corrections_set
	print(f"{timeis()} {green}making spelling mistakes set", end=" ")
	sp_mistakes_df = pd.read_csv(
		"sandhi/spelling mistakes.csv", dtype=str, header=None, sep="\t")
	sp_mistakes_df.fillna("", inplace=True)

	spelling_mistakes_set = set(sp_mistakes_df[0].tolist())
	print(f"{white}{len(spelling_mistakes_set)}")

	filter = sp_mistakes_df[0] == sp_mistakes_df[1]
	duplicates_df = sp_mistakes_df[filter]
	duplicates_list = duplicates_df[0].to_list()
	if duplicates_list != []:
		print(f"{timeis()} {red}! dupes found {duplicates_list}")

	print(f"{timeis()} {green}making spelling corrections set", end=" ")
	spelling_corrections_set = set(sp_mistakes_df[1].tolist())
	remove_me = set()
	add_me = set()

	for word in spelling_corrections_set:
		if re.findall(".+ .+", word):
			remove_me.add(word)
			single_words = word.split(" ")
			for single_word in single_words:
				add_me.add(single_word)

	spelling_corrections_set = spelling_corrections_set - remove_me
	spelling_corrections_set = spelling_corrections_set | add_me
	print(f"{white}{len(spelling_corrections_set)}")

	f2 = open("output/sandhi/matches.csv", "w")
	f2.write(f"word\tsplit\tprocess\trules\n")

	for row in range(len(sp_mistakes_df)):
		mistake = sp_mistakes_df.loc[row, 0]
		correction = sp_mistakes_df.loc[row, 1]
		f2.write(f"{mistake}\tincorrect spelling of <i>{correction}</i>\tspelling\tsp\n")
	f2.close()


def make_variant_readings_set():
	global variant_readings_set
	global variant_corrections_set

	print(f"{timeis()} {green}making variant readings set", end=" ")
	variant_reading_df = pd.read_csv(
		"sandhi/variant readings.csv", dtype=str, header=None, sep="\t")
	variant_reading_df.fillna("", inplace=True)

	variant_readings_set = set(variant_reading_df[0].tolist())
	print(f"{white}{len(variant_readings_set)}")

	filter = variant_reading_df[0] == variant_reading_df[1]
	duplicates_df = variant_reading_df[filter]
	duplicates_list = duplicates_df[0].to_list()
	if duplicates_list != []:
		print(f"{timeis()} {red}! dupes found {duplicates_list}")

	print(f"{timeis()} {green}making variant corrections set", end=" ")
	variant_corrections_set = set(variant_reading_df[1].tolist())
	remove_me = set()
	add_me = set()

	for word in variant_corrections_set:
		if re.findall(".+ .+", word):
			remove_me.add(word)
			single_words = word.split(" ")
			for single_word in single_words:
				add_me.add(single_word)

	variant_corrections_set = variant_corrections_set - remove_me
	variant_corrections_set = variant_corrections_set | add_me
	print(f"{white}{len(variant_corrections_set)}")

	f2 = open("output/sandhi/matches.csv", "a")

	for row in range(len(variant_reading_df)):
		variant = variant_reading_df.loc[row, 0]
		correction = variant_reading_df.loc[row, 1]
		f2.write(f"{variant}\tvariant reading of <i>{correction}</i>\tvariant\tv\n")
	f2.close()


def make_abbreviations_and_neg_set():
	
	print(f"{timeis()} {green}making abbreviations set", end=" ")
		
	global dpd_df
	global dpd_df_length

	global abbreviations_set
	abbreviations_set = []
	
	global neg_headwords_set
	neg_headwords_set = []

	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)
	dpd_df_length = len(dpd_df)

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(r" \d*$", "", headword)
		pos = dpd_df.loc[row, "POS"]
		neg = dpd_df.loc[row, "Neg"]

		if pos == "abbrev":
			abbreviations_set.append(headword_clean)

		if neg == "neg":
			neg_headwords_set.append(headword)

	abbreviations_set = set(abbreviations_set)
	
	print(f"{white}{len(abbreviations_set)}")
	print(f"{timeis()} {green}making neg headwords set", end=" ")
	print(f"{white}{len(neg_headwords_set)}")


def make_manual_corrections_set():
	
	print(f"{timeis()} {green}making manual corrections set", end=" ")
	
	global manual_corrections_set
	manual_corrections_df = pd.read_csv("sandhi/manual corrections.csv", dtype=str, header=None, sep="\t")
	manual_corrections_df.fillna("", inplace=True)

	manual_corrections_set = set(manual_corrections_df[0].tolist())
	print(f"{white}{len(manual_corrections_set)}")

	manual_corrections_list = manual_corrections_df[1].tolist()

	for word in manual_corrections_list:
		if not re.findall ("\\+", word):
			print(f"{timeis()} {red}! no plus sign {word}")
		if re.findall ("(\\S\\+|\\+\\S)", word):
			print(f"{timeis()} {red}! needs space {word}")					
	
	f2 = open("output/sandhi/matches.csv", "a")

	for row in range(len(manual_corrections_df)):
		sandhi = manual_corrections_df.loc[row, 0]
		split = manual_corrections_df.loc[row, 1]
		f2.write(f"{sandhi}\t{split}\tmanual\tm\n")
	f2.close()


def make_shortlist_set():

	global shortlist_set
	print(f"{timeis()} {green}making shortlist set", end=" ")
	
	shortlist_df = pd.read_csv("sandhi/shortlist.csv", dtype=str, header=None, sep="\t")
	shortlist_df.fillna("", inplace=True)

	shortlist_set = set(shortlist_df[0].tolist())
	print(f"{white}{len(shortlist_set)}")


def import_text_set():

	global text_set
	print(f"{timeis()} {green}importing text set", end=" ")

	with open(f"output/set text", "rb") as p:
		text_set = pickle.load(p)
	
	text_set = text_set | sc_text_set
	text_set = text_set | spelling_corrections_set
	text_set = text_set | variant_corrections_set
	text_set = text_set - spelling_mistakes_set
	text_set = text_set - variant_readings_set
	text_set = text_set - abbreviations_set
	text_set = text_set - manual_corrections_set

	print(f"{white}{len(text_set)}")
	

def make_all_inflections_set():

	print(f"{timeis()} {green}making all inflections set", end=" ")

	global all_inflections_dict
	global all_inflections_set
	all_inflections_set = set()
	
	global neg_inflections_set
	neg_inflections_set = set()
	
	exceptions_list = ["abbrev", "cs", "idiom", "letter", "prefix", "root", "sandhi", "suffix", "ve"]

	with open("output/all inflections dict", "rb") as f:
		all_inflections_dict = pickle.load(f)

	for headword in all_inflections_dict:
		if all_inflections_dict[headword]["pos"] not in exceptions_list:
			inflections_set = all_inflections_dict[headword]["inflections"]
			for inflection in inflections_set:
				all_inflections_set.add(inflection)
				if headword in neg_headwords_set:
					neg_inflections_set.add(inflection)
	
	print(f"{white} {len(all_inflections_set)}")
	print(f"{timeis()} {green}making neg inflections set {white} {len(neg_inflections_set)}")
			
def make_all_inflections_nfl_nll():

		print(f"{timeis()} {green}making all inflections nfl & nll", end=" ")

		global all_inflections_nofirst
		global all_inflections_nolast
		global all_inflections_first3
		global all_inflections_last3

		all_inflections_nofirst = []
		all_inflections_nolast = []
		all_inflections_first3 = []
		all_inflections_last3 = []
		
		sorted_set = sorted(set(all_inflections_set))
		for inflection in sorted_set:
			all_inflections_nofirst += [inflection.replace(inflection[0], "")] # no first letter
			all_inflections_nolast += [inflection.replace(inflection[-1], "")] # no last letter
			all_inflections_first3 += [inflection.replace(inflection[3:], "")]  # leave first 3 letters
			all_inflections_last3 += [inflection.replace(inflection[:-3], "")]  # leave last 3 letters
		
		print(f"{white}{len(all_inflections_nofirst)}")
		

def make_unmatched_set():

	print(f"{timeis()} {green}making unmatched set", end = " ")
	
	global unmatched_set
	unmatched_set = text_set - set(all_inflections_set)
	
	print(f"{white}{len(unmatched_set)}")


def import_sandhi_rules():

	print(f"{timeis()} {green}importing sandhi rules", end=" ")
	
	rules_df = pd.read_csv("sandhi/sandhi rules.csv", sep="\t", dtype = str)
	rules_df.fillna("", inplace = True)
	
	print(f"{white}{len(rules_df)}")
	
	global rules
	rules = rules_df.to_dict('index')

	print(f"{timeis()} {green}testing sandhi rules for dupes", end = " ")

	dupes = rules_df[rules_df.duplicated(
		["chA", "chB", "ch1", "ch2"], keep=False)]

	if len(dupes) != 0:
		print(f"\n{timeis()} {red}! duplicates found! please remove them and try again")
		print(f"{timeis()} {red}{line}")
		print(f"\n{red}{dupes}")
		sys.exit()

	else:
		print(f"{white}ok")

	print(f"{timeis()} {green}testing sandhi rules for spaces", end=" ")

	if \
	rules_df["chA"].str.contains(" ").any() or \
    rules_df["chB"].str.contains(" ").any() or \
    rules_df["ch1"].str.contains(" ").any() or \
    rules_df["ch2"].str.contains(" ").any():
		print(f"\n{timeis()} {red}! spaces found! please remove them and try again")
		print(f"{timeis()} {red}{line}")
		sys.exit()

	else:
		print(f"{white}ok")



def remove_exceptions():

	print(f"{timeis()} {green}removing exceptions", end=" ")

	exceptions_df = pd.read_csv("sandhi/sandhi exceptions.csv", header = None)
	exceptions_set = set(exceptions_df[0].tolist())
	
	global unmatched_set
	unmatched_set = set(unmatched_set) - exceptions_set
	
	global all_inflections_set
	all_inflections_set = set(all_inflections_set) - exceptions_set 
	
	print(f"{white}{len(exceptions_set)}")



def two_word_sandhi():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}two word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/process2.csv", "w")
	f2 = open("output/sandhi/matches.csv", "a")

	global matches2
	matches2 = []
	counter = 0
	length = len(unmatched_set)

	for word in unmatched_set:
		
		if counter % 1000 == 0:
			print(f"{timeis()} {counter}/{length}\t{word}")

		f1.write(f"{word}\n")

		for x in range(0, len(word)-1):
			wordA = word[:-x-1]
			wordB = word[-1-x:]
			wordA_lastletter = wordA[len(wordA)-1]
			wordB_firstletter = wordB[0]
			f1.write(f"\t{wordA}\t{wordB}\n")

			# blah blah

			if wordA in all_inflections_set and \
			wordB in all_inflections_set:
				f1.write(f"\t{wordA}\t{wordB}\t-\t-\tmatch\n")
				f2.write(f"{word}\t{wordA}-{wordB}\ttwo-word\t0\n")
				matches2.append(word)
			
			# bla* *lah
			
			for rule in rules:
				chA = rules[rule].get("chA")
				chB = rules[rule].get("chB")	
				ch1 = rules[rule].get("ch1")
				ch2 = rules[rule].get("ch2")
				
				if wordA_lastletter == chA and \
				wordB_firstletter == chB:
					word1 = wordA[:-1] + ch1
					word2 = ch2 + wordB[1:]

					if word1 in all_inflections_set and \
					word2 in all_inflections_set:
						matches2.append(word)
						f1.write(f"\t{word1}\t{word2}\t{rule+2}\t-\tmatch\n")
						f2.write(f"{word}\t{word1}-{word2}\ttwo-word\t{rule+2}\n")
						
		counter += 1

	print(f"{timeis()} {green}two word matches {white}{len(matches2)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches2.csv", "w") as f:
		for word in matches2:
			f.write(f"{word}\n")

	global unmatched2
	unmatched2 = set(unmatched_set) - set(matches2)
	with open ("output/sandhi/unmatched2.csv", "w") as f:
		for word in unmatched2:
			f.write(f"{word}\n")

	print(f"{timeis()} {green}two word unmatched {white}{len(unmatched2)}")


def three_word_sandhi():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}three word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/process3.csv", "w")
	f2 = open("output/sandhi/matches.csv", "a")

	global matches3
	matches3 = []
	counter = 0
	length = len(unmatched2)

	for word in unmatched2:
		
		if counter % 100 == 0:
			print(f"{timeis()} {counter}/{length}\t{word}")
		
		f1.write(f"{counter}\t{word}\n")

		for x in range(0, len(word)-1):
			wordA = word[:-x-1]
			wordA_lastletter = wordA[len(wordA)-1]
			
			for y in range(0, len(word[-1-x:])-1):
				wordB = word[-1-x:-y-1]
				wordB_firstletter = wordB[0]
				wordB_lastletter = wordB[len(wordB)-1]
				wordC = word[-1-y:]
				wordC_firstletter = wordC[0]
				f1.write(
					f"\t{wordA}\t{wordB}\t{wordC}\t{wordA_lastletter}|{wordB_firstletter}|{wordB_lastletter}|{wordC_firstletter}\n")

				# blah blah blah

				if \
				wordA in all_inflections_set and \
				wordB in all_inflections_set and \
				wordC in all_inflections_set:

					matches3.append(word)
					f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t-\t-\tmatch\n")
					f2.write(f"{word}\t{wordA}-{wordB}-{wordC}\tthree-word\t0,0\n")

				# blah bla* *lah

				if wordA in all_inflections_set:

					for rule in rules:
						chA = rules[rule].get("chA")
						chB = rules[rule].get("chB")
						ch1 = rules[rule].get("ch1")
						ch2 = rules[rule].get("ch2")

						if wordB_lastletter == chA and \
						wordC_firstletter == chB:
							word2 = wordB[:-1] + ch1
							word3 = ch2 + wordC[1:]

							if wordA in all_inflections_set and \
							word2 in all_inflections_set and \
							word3 in all_inflections_set:
								matches3.append(word)
								f1.write(f"\t{wordA}\t{word2}\t{word3}\t-\t{rule+2}\tmatch\n")
								f2.write(f"{word}\t{wordA}-{word2}-{word3}\tthree-word\t0,{rule+2}\n")
				
				# bla* *lah blah

				if wordC in all_inflections_set:
					
					for rule in rules:
						chA = rules[rule].get("chA")
						chB = rules[rule].get("chB")
						ch1 = rules[rule].get("ch1")
						ch2 = rules[rule].get("ch2")

						if wordA_lastletter == chA and \
						wordB_firstletter == chB:
							word1 = wordA[:-1] + ch1
							word2 = ch2 + wordB[1:]

							if word1 in all_inflections_set and \
							word2 in all_inflections_set and \
							wordC in all_inflections_set:
								matches3.append(word)
								f1.write(f"\t{word1}\t{word2}\t{wordC}\t{rule+2}\t-\tmatch\n")
								f2.write(f"{word}\t{word1}-{word2}-{wordC}\tthree-word\t{rule+2},0\n")

				# bla* *la* *lah
				
				for rulex in rules:
					chAx = rules[rulex].get("chA")
					chBx = rules[rulex].get("chB")
					ch1x = rules[rulex].get("ch1")
					ch2x = rules[rulex].get("ch2")

					if wordA_lastletter == chAx and \
					wordB_firstletter == chBx:
						word1 = wordA[:-1] + ch1x
						word2 = ch2x + wordB[1:]
					
						for ruley in rules:
							chAy = rules[ruley].get("chA")
							chBy = rules[ruley].get("chB")
							ch1y = rules[ruley].get("ch1")
							ch2y = rules[ruley].get("ch2")

							if wordB_lastletter == chAy and \
							wordC_firstletter == chBy:
								word2 = (ch2x + wordB[1:])[:-1] + ch1y
								word3 = ch2y + wordC[1:]

								if word1 in all_inflections_set and \
								word2 in all_inflections_set and \
								word3 in all_inflections_set:
									matches3.append(word)
									f1.write(f"\t{word1}\t{word2}\t{word3}\t{rulex+2}\t{ruley+2}\tmatch\n")
									f2.write(f"{word}\t{word1}-{word2}-{word3}\tthree-word\t{rulex+2},{ruley+2}\n")
												
		counter += 1

	print(f"{timeis()} {green}three word matches {white}{len(matches3)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches3.csv", "w") as f:
		for word in matches3:
			f.write(f"{word}\n")

	global unmatched3
	unmatched3 = set(unmatched2) - set(matches3)
	with open("output/sandhi/unmatched3.csv", "w") as f:
		for word in unmatched3:
			f.write(f"{word}\n")

	print(f"{timeis()} {green}three word unmatched {white}{len(unmatched3)}")


def four_word_sandhi():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}four word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/process4.csv", "w")
	f2 = open("output/sandhi/matches.csv", "a")

	global matches4
	matches4 = []
	counter = 0
	length=len(unmatched3)

	for word in unmatched3:

		if counter % 10 == 0:
			print(f"{timeis()} {counter}/{length}\t{word}")

		f1.write(f"{counter}\t{word}\n")

		for x in range(0, len(word)-1):
			wordA = word[:-x-1]
			wordA_lastletter = wordA[len(wordA)-1]

			for y in range(0, len(word[-1-x:])-1):
				wordB = word[-1-x:-y-1]
				wordB_firstletter = wordB[0]
				wordB_lastletter = wordB[len(wordB)-1]
				wordC = word[-1-y:]
				wordC_firstletter = wordC[0]

				for z in range(0, len(word[-1-y:])-1):
					wordC = word[-1-y:-z-1]
					wordC_firstletter = wordC[0]
					wordC_lastletter = wordC[len(wordC)-1]
					wordD = word[-1-z:]
					wordD_firstletter = wordD[0]
					f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\n") # \t{wordA_lastletter}|{wordB_firstletter}|{wordB_lastletter}|{wordC_firstletter}|{wordC_lastletter}|{wordD_firstletter}\n")

					# blah blah blah blah

					if wordA in all_inflections_set and \
					wordB in all_inflections_set and \
					wordC in all_inflections_set and \
					wordD in all_inflections_set:
						matches4.append(word)
						f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\t-\t-\t-\tmatch\n")
						f2.write(f"{word}\t{wordA}-{wordB}-{wordC}-{wordD}\tfour-word\t0,0,0\n")

					# blah blah bla* *lah

					if wordA in all_inflections_set and \
					wordB in all_inflections_set:
							
						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if wordC_lastletter == chA and \
							wordD_firstletter == chB:
								word3 = wordC[:-1] + ch1
								word4 = ch2 + wordD[1:]

								if word3 in all_inflections_set and \
								word4 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{wordA}\t{wordB}\t{word3}\t{word4}\t-\t-\t{rule+2}\tmatch\n")
									f2.write(f"{word}\t{wordA}-{wordB}-{word3}-{word4}\tfour-word\t0,0,{rule+2}\n")

					# bla* *lah blah blah

					if wordC in all_inflections_set and \
					wordD in all_inflections_set:

						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if wordA_lastletter == chA and \
							wordB_firstletter == chB:
								word1 = wordA[:-1] + ch1
								word2 = ch2 + wordB[1:]

								if word1 in all_inflections_set and \
								word2 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{word1}\t{word2}\t{wordC}\t{wordD}\t{rule+2}-\t-\t\tmatch\n")
									f2.write(f"{word}\t{word1}-{word2}-{wordC}-{wordD}\tfour-word\t{rule+2},0,0\n")

					# blah bla* *lah blah

					if wordA in all_inflections_set and \
					wordD in all_inflections_set:

						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if wordB_lastletter == chA and \
							wordC_firstletter == chB:
								word2 = wordB[:-1] + ch1
								word3 = ch2 + wordC[1:]

								if word2 in all_inflections_set and \
								word3 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{wordA}\t{word2}\t{word3}\t{wordD}\t-\t{rule+2}\t-\tmatch\n")
									f2.write(f"{word}\t{wordA}-{word2}-{word3}-{wordD}\tfour-word\t0,{rule+2},0\n")
					
					# blah bla* *la* *lah

					if wordA in all_inflections_set:

						for rulex in rules:
							chAx = rules[rulex].get("chA")
							chBx = rules[rulex].get("chB")
							ch1x = rules[rulex].get("ch1")
							ch2x = rules[rulex].get("ch2")

							if wordB_lastletter == chAx and \
							wordC_firstletter == chBx:
								word2 = wordB[:-1] + ch1x
								word3 = ch2x + wordC[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if wordC_lastletter == chAy and \
									wordD_firstletter == chBy:
										word3 = (ch2x + wordC[1:])[:-1] + ch1y
										word4 = ch2y + wordD[1:]

										if word2 in all_inflections_set and \
										word3 in all_inflections_set and \
										word4 in all_inflections_set:
											matches4.append(word)
											f1.write(f"\t{wordA}\t{word2}\t{word3}\t{word4}\t-\t{rulex+2}\t{ruley+2}\tmatch\n")
											f2.write(f"{word}\t{wordA}-{word2}-{word3}-{word4}\tfour-word\t0,{rulex+2},{ruley+2}\n")

					# bla* *la* *lah blah

					if wordD in all_inflections_set:

						for rulex in rules:
							chAx = rules[rulex].get("chA")
							chBx = rules[rulex].get("chB")
							ch1x = rules[rulex].get("ch1")
							ch2x = rules[rulex].get("ch2")

							if wordA_lastletter == chAx and \
							wordB_firstletter == chBx:
								word1 = wordA[:-1] + ch1x
								word2 = ch2x + wordB[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if wordB_lastletter == chAy and \
									wordC_firstletter == chBy:
										word2 = (ch2x + wordB[1:])[:-1] + ch1y
										word3 = ch2y + wordC[1:]

										if word1 in all_inflections_set and \
										word2 in all_inflections_set and \
										word3 in all_inflections_set:
											matches4.append(word)
											f1.write(f"\t{word1}\t{word2}\t{word3}\t{wordD}\t{rulex+2}\t{ruley+2}\t-\tmatch\n")
											f2.write(f"{word}\t{word1}-{word2}-{word3}-{wordD}\tfour-word\t{rulex+2},{ruley+2},0\n")

					# bla* *lah bla* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if wordA_lastletter == chAx and \
						wordB_firstletter == chBx:
							word1 = wordA[:-1] + ch1x
							word2 = ch2x + wordB[1:]

							for ruley in rules:
								chAy = rules[ruley].get("chA")
								chBy = rules[ruley].get("chB")
								ch1y = rules[ruley].get("ch1")
								ch2y = rules[ruley].get("ch2")

								if wordC_lastletter == chAy and \
								wordD_firstletter == chBy:
									word3 = wordC[:-1] + ch1y
									word4 = ch2y + wordD[1:]

									if word1 in all_inflections_set and \
									word2 in all_inflections_set and \
									word3 in all_inflections_set and \
									word4 in all_inflections_set:
										matches4.append(word)
										f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t-\t{ruley+2}\tmatch\n")
										f2.write(f"{word}\t{word1}-{word2}-{word3}-{word4}\tfour-word\t{rulex+2},0,{ruley+2}\n")

					# bla* *la* *la* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if wordA_lastletter == chAx and \
						wordB_firstletter == chBx:
							word1 = wordA[:-1] + ch1x
							word2 = ch2x + wordB[1:]

							for ruley in rules:
								chAy = rules[ruley].get("chA")
								chBy = rules[ruley].get("chB")
								ch1y = rules[ruley].get("ch1")
								ch2y = rules[ruley].get("ch2")

								if wordB_lastletter == chAy and \
								wordC_firstletter == chBy:
									word2 = (ch2x + wordB[1:])[:-1] + ch1y
									word3 = ch2y + wordC[1:]

									for rulez in rules:
										chAz = rules[rulez].get("chA")
										chBz = rules[rulez].get("chB")
										ch1z = rules[rulez].get("ch1")
										ch2z = rules[rulez].get("ch2")

										if wordC_lastletter == chAz and \
										wordD_firstletter == chBz:
												word3 =(ch2y + wordC[1:])[:-1] + ch1z
												word4 = ch2z + wordD[1:]

												if word1 in all_inflections_set and \
												word2 in all_inflections_set and \
												word3 in all_inflections_set and \
												word4 in all_inflections_set:
													matches4.append(word)
													f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t{ruley+2}\t{rulez+2}\tmatch\n")
													f2.write(f"{word}\t{word1}-{word2}-{word3}-{word4}\tfour-word\t{rulex+2},{ruley+2},{rulez+2}\n")

		counter += 1

	print(f"{timeis()} {green}four word matches {white}{len(matches4)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches4.csv", "w") as f:
		for word in matches4:
			f.write(f"{word}\n")

	global unmatched4
	unmatched4 = set(unmatched3) - set(matches4)
	with open("output/sandhi/unmatched4.csv", "w") as f:
		for word in unmatched4:
			f.write(f"{word}\n")
			
	print(f"{timeis()} {green}four word unmatched {white}{len(unmatched4)}")



def split_from_front_and_back(word_initial, word_front, word, word_back, comment, rules_front, rules_back):

	f1 = open("output/sandhi/processxfront.csv", "a")
	f2 = open("output/sandhi/matches.csv", "a")

	f1.write(f"{word_initial}\t{word_front}\t{word}\t{word_back}\t({comment})\n")
	# f1.write(f"\ttried: [{len(tried)}] [{tried}]\n")
	if printme:
		print(f"{timeis()} word: {yellow}{word_initial} : {green}{word_front}{blue}{word}{green}{word_back} {white}({comment})")
		print(f"{timeis()} tried: [{len(tried)}] {tried}")

	# first test if word is in tried

	tried_front = re.sub(fr"^(.+\-)*(.+\-)$", fr"\2", word_front)
	tried_back = re.sub(fr"^(\-.+?)\-(.+)*$", fr"\1", word_back)

	if f"{tried_front}{word}{tried_back}" in tried:
		f1.write(f"\ttried already!\t{tried_front}{word}{tried_back}\n")
		if printme:
			print(f"{timeis()} tried already!: {red}{tried_front}{word}{tried_back}")

	else:
		tried.append(f"{tried_front}{word}{tried_back}")
		f1.write(f"\ttried new\t{tried_front}{word}{tried_back}\n")
		if printme:
			print(f"{timeis()} tried new: {tried_front}{word}{tried_back}")

		word_front_original = word_front
		word_back_original = word_back
		lwff_clean = ""
		lwff_fuzzy = ""
		comment = ""

		# is word a match?

		if word in all_inflections_set:
			matchesx.append(word_initial)
			f1.write(f"\tmatch!\t{word_initial}\t{word_front}{word}{word_back}\n")
			f2.write(f"{word_initial}\t{word_front}{word}{word_back}\tx-wordfront\t{rules_front + rules_back}\n")
			if printme:
				print(f"{timeis()} {red}match! {yellow}{word_front}{blue}{word}{green}{word_back}")

		else:

			# does word end in api eva iti?

			apievaiti = re.findall("(pi|va|ti)$", word)

			if apievaiti != []:

				f1.write(f"\n\t{apievaiti}\n")
				if printme:
					print(f"{timeis()} api eva iti: {apievaiti}")

				try:
					if word[-3] in vowels:
						wordA = word[:-3]
						wordB = word[-3:]

					else:
						wordA = word[:-2]
						wordB = word[-2:]

				except:
					wordA = word[:-2]
					wordB = word[-2:]

				if printme:
					print(f"{timeis()} api eva iti: {wordA}\t{wordB}")

				for rule in rules:
					chA = rules[rule].get("chA")
					chB = rules[rule].get("chB")
					ch1 = rules[rule].get("ch1")
					ch2 = rules[rule].get("ch2")

					try:
						wordA_lastletter = wordA[-1]
					except:
						wordA_lastletter = wordA
					wordB_firstletter = wordB[0]

					if wordA_lastletter == chA and \
					wordB_firstletter == chB:
						word1 = wordA[:-1] + ch1
						word2 = ch2 + wordB[1:]
						f1.write(f"\tapicaeveiti\t{word1}\t{word2}\n")

						if \
						word2 == "api" or \
						word2 == "eva" or \
						word2 == "iti":
							word_to_recurse = word1
							word_back_to_recurse = f"-{word2}{word_back_original}"
							f1.write(f"\tapicaeveiti fin:\t{word_front}\t{word_to_recurse}\t{word_back}\n")
							if printme:
								print(f"{timeis()} apieveiti fin: {green}{word_front}{blue}{word_to_recurse}{yellow}{word_back_to_recurse}\n")
							comment = "api ca eva iti"
							rules_back_to_recurse = [rule+2] + rules_back
							split_from_front_and_back(word_initial, word_front, word_to_recurse, word_back_to_recurse, comment, rules_front, rules_back_to_recurse)

			else:

				# find longest fuzzy words from the front
				
				def find_longest_word_fuzzy(word):

					lwff_fuzzy_list = []
					lwfb_fuzzy_list = []
					f1.write(f"\n")

					for x in range(len(word)-1): # one letter front, one back
						wordA = word[:1+x]
						wordB = word[1+x:]

						fuzzy_searchA = wordA[:-1] in all_inflections_nolast
						f1.write(f"\tfuzzysearchA\t{fuzzy_searchA}\n")
						if printme:
							print(f"{timeis()} fuzzysearchA\t{fuzzy_searchA}")

						if fuzzy_searchA == True and \
						len(wordA) > 0 and \
						lwff_fuzzy_list == []:
							lwff_fuzzy_list = [wordA]
						
						elif \
						fuzzy_searchA == True and \
						len(wordA) > 0 and \
						lwff_fuzzy_list != []:
							lwff_fuzzy_list = [wordA] + lwff_fuzzy_list

						fuzzy_searchB = wordB[1:] in all_inflections_nofirst
						f1.write(f"\tfuzzysearchB\t{fuzzy_searchB}\n")
						if printme:
							print(f"{timeis()} fuzzysearchB\t{fuzzy_searchB}")

						if \
						fuzzy_searchB == True and \
						len(wordB) > 0 and \
						lwfb_fuzzy_list  == []:
							lwfb_fuzzy_list = [wordB]
						
						elif \
						fuzzy_searchB == True and \
						len(wordB) > 0 and \
						lwfb_fuzzy_list  != []:
							lwfb_fuzzy_list = [wordB] + lwfb_fuzzy_list


					lwff_fuzzy_list = sorted(set(lwff_fuzzy_list), key=len, reverse=True)
					lwfb_fuzzy_list = sorted(set(lwfb_fuzzy_list), key=len, reverse=True)

					f1.write(f"\tlwff_fuzzy list\t{lwff_fuzzy_list}\n")
					f1.write(f"\tlwfb_fuzzy list\t{lwfb_fuzzy_list}\n")
					if printme:
						print(f"{timeis()} lwff-fuzzy list\t{lwff_fuzzy_list}")
						print(f"{timeis()} lwfb-fuzzy\t{lwfb_fuzzy_list}")

					return [lwff_fuzzy_list, lwfb_fuzzy_list]
				
				fuzzy_list = find_longest_word_fuzzy(word)

				lwff_fuzzy_list = fuzzy_list[0]
				lwfb_fuzzy_list = fuzzy_list[1]

				# split fuzzy front, run rules and recurse

				for lwff_fuzzy in lwff_fuzzy_list:

					if \
					(len(lwff_fuzzy) > 2 and \
					lwff_fuzzy == lwff_fuzzy_list[0]) or \
					lwff_fuzzy in shortlist_set:
					
						f1.write(f"\n\tlwff_fuzzy\t{lwff_fuzzy}\n")
						if printme:
							print(f"{timeis()} lwff_fuzzy\t{lwff_fuzzy}")

						try:
							if (lwff_fuzzy[-1]) in vowels:
								wordA_fuzzy = (lwff_fuzzy[:-1])
							else:
								wordA_fuzzy = (lwff_fuzzy)
						except:
							wordA_fuzzy = (lwff_fuzzy)
						
						wordB_fuzzy = re.sub(f"^{wordA_fuzzy}", "", word)
						try:
							wordA_lastletter = wordA_fuzzy[-1]
						except:
							wordA_lastletter = ""
						try:
							wordB_firstletter = wordB_fuzzy[0]
						except:
							wordB_firstletter = ""
						if printme:
							print(f"{timeis()} {wordA_lastletter}-{wordB_firstletter}")

						for rule in rules:

							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")
							
							if \
							wordA_lastletter == chA and \
							wordB_firstletter == chB:
								word1 = wordA_fuzzy[:-1] + ch1
								word2 = ch2 + wordB_fuzzy[1:]

								f1.write(f"\tfuzzy words front:\t{word1}-{word2}\n")
								if printme:  
									print(f"{timeis()} fuzzy words front: {green}{word1}-{blue}{word2}")

								if word1 in all_inflections_set:
									test = word2[:3] in all_inflections_first3
									f1.write(f"\ttestword2\t{test}\n")
									if printme:  
										print(f"{timeis()} testword2\t{test}")

									if test == True:	
										word_to_recurse = word2
										word_front_to_recurse = f"{word_front_original}{word1}-"
										f1.write(f"\tfuzzy fin:\t{word_front}\t{word_to_recurse}\t{word_back}\n")
										if printme:
											print(f"{timeis()} fuzzy: {green}{word_front}{blue}{word_to_recurse}\t{word_back}\n")
										comment = "front fuzzy"
										rules_front_to_recurse = rules_front + [rule+2]
										split_from_front_and_back(word_initial, word_front_to_recurse, word_to_recurse, word_back, comment, rules_front_to_recurse, rules_back)
			
				# split fuzzy back, run rules and recurse

				for lwfb_fuzzy in lwfb_fuzzy_list:
					if (len(lwfb_fuzzy) > 2 and \
                    lwfb_fuzzy == lwfb_fuzzy_list[0]) or \
					lwfb_fuzzy in shortlist_set:

						f1.write(f"\n\tlwfb_fuzzy\t{lwfb_fuzzy}\n")
						if printme:
							print(f"{timeis()} lwfb_fuzzy\t{lwfb_fuzzy}")
						
						wordB_fuzzy = (lwfb_fuzzy)
						wordA_fuzzy = re.sub(f"{wordB_fuzzy}", "", word)

						try:
							wordA_lastletter = wordA_fuzzy[-1]
						except:
							wordA_lastletter = ""
						try:
							wordB_firstletter = wordB_fuzzy[0]
						except:
							wordB_firstletter = ""
						if printme:
							print(f"{timeis()} {wordA_lastletter}-{wordB_firstletter}")

						for rule in rules:

							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if wordA_lastletter == chA and \
							wordB_firstletter == chB:
								word1 = wordA_fuzzy[:-1] + ch1
								word2 = ch2 + wordB_fuzzy[1:]

								f1.write(f"\tfuzzy words back:\t{word1}-{word2}\n")
								if printme:
									print(f"{timeis()} fuzzy words back: {green}{word1}-{blue}{word2}")

								if word2 in all_inflections_set:
									test = word2[-3:] in all_inflections_last3
									f1.write(f"\ttestword1\t{test}\n")
									if printme:
										print(f"{timeis()} testword1\t{test}")

									if test == True:
										word_to_recurse = word1
										word_back_to_recurse = f"-{word2}{word_back_original}"
										f1.write(
											f"\tfuzzy back fin:\t{word_front_original}\t{word_to_recurse}\t{word_back_to_recurse}\n")
										if printme:
											print(
												f"{timeis()} fuzzy back: {green}{word_front_original}{blue}{word_to_recurse}\t{word_back_to_recurse}\n")
										comment = "back fuzzy"
										rules_back_to_recurse =  [rule+2] + rules_back
										split_from_front_and_back(word_initial, word_front_original, word_to_recurse, word_back_to_recurse, comment, rules_front, rules_back_to_recurse)

				# find longest clean word from the front

				def find_longest_word_clean(word):

					lwff_clean_list = []
					lwfb_clean_list = []

					for x in range(len(word)-3): # two letters front, two back
						wordA = word[:2+x]
						wordB = word[2+x:]

						clean_searchA = wordA in all_inflections_set

						if clean_searchA != False and \
						len(wordA) > 0 and \
						lwff_clean_list == []:
							lwff_clean_list = [wordA]

						elif \
						clean_searchA != False and \
						len(wordA) > 0 and \
						lwff_clean_list != []:
							lwff_clean_list = [wordA] + lwff_clean_list
						
						clean_searchB = wordB in all_inflections_set

						if clean_searchB != False and \
						len(wordB) > 0 and \
						lwfb_clean_list == []:
							lwfb_clean_list = [wordB]
						
						elif \
						clean_searchB != False and \
						len(wordB) > 0 and \
						lwfb_clean_list != []:
							lwfb_clean_list = [wordB] + lwfb_clean_list

					lwff_clean_list = sorted(set(lwff_clean_list), key=len, reverse=True)
					lwfb_clean_list = sorted(set(lwfb_clean_list), key=len, reverse=True)

					f1.write(f"\n\tlwff_clean_list\t{lwff_clean_list}\n")
					f1.write(f"\tlwfb_clean_list\t{lwfb_clean_list}\n")
					if printme:
						print(f"{timeis()} lwff_clean\t{lwff_clean_list}")
						print(f"{timeis()} lwfb_clean\t{lwfb_clean_list}")

					return [lwff_clean_list, lwfb_clean_list]

				clean_list = find_longest_word_clean(word)
				lwff_clean_list = clean_list[0]
				lwfb_clean_list = clean_list[1]

				# split clean front, run rules and recurse

				for lwff_clean in lwff_clean_list:
					
					if (len(lwff_clean) > 2 and \
                    lwff_clean == lwff_clean_list[0]) or \
					lwff_clean in shortlist_set:

						wordA = lwff_clean
						wordB = re.sub(f"^{wordA}", "", word)
						f1.write(f"\n\tclean words front:\t{wordA}\t{wordB}\n")
						if printme:
							print(f"{timeis()} clean words front: {green}{wordA}-{blue}{wordB}")

						test = wordB[:3] in all_inflections_first3
						f1.write(f"\ttestB\t{test}\n")
						if printme:
							print(f"{timeis()} testB\t{test}")

						if test == True:
							word_to_recurse = re.sub(f"^{wordA}", "", word)
							word_front_to_recurse = f"{word_front_original}{wordA}-"
							f1.write(f"\tclean front fin\t{word_front_to_recurse}\t{word_to_recurse}\t{word_back}\n")
							if printme:
								print(f"{timeis()} clean front fin: {green}{word_front_to_recurse}{blue}{word_to_recurse}\t{word_back}\n")
							comment = "front clean"
							rules_front_to_recurse = rules_front + [0]
							split_from_front_and_back(word_initial, word_front_to_recurse, word_to_recurse, word_back, comment, rules_front_to_recurse, rules_back)
					
				# lwfb

				for lwfb_clean in lwfb_clean_list:

					if (len(lwfb_clean) > 3 and \
					lwfb_clean == lwfb_clean_list[0]) or \
					lwfb_clean in shortlist_set:

						wordB = lwfb_clean
						wordA = re.sub(f"{wordB}$", "", word)
						f1.write(f"\n\tclean words back:\t{wordA}\t{wordB}\n")
						if printme:
							print(f"{timeis()} clean words back: {green}{wordA}-{blue}{wordB}")

						test = wordA[-3:] in all_inflections_last3
						f1.write(f"\ttestA\t{test}\n")
						if printme:
							print(f"{timeis()} testA\t{test}")

						if test == True:

							word_front = word_front_original
							word_to_recurse = wordA
							word_back_to_recurse = f"-{wordB}{word_back_original}"
							f1.write(f"\tclean back fin\t{word_front}\t{word_to_recurse}\t{word_back}\n")
							if printme:
								print(f"{timeis()} clean back fin: {green}{word_front}{blue}{word_to_recurse}\t{word_back}\n")
							comment = "back clean"
							rules_back_to_recurse = [0] + rules_back
							split_from_front_and_back(word_initial, word_front, word_to_recurse, word_back_to_recurse, comment, rules_front, rules_back_to_recurse)
			
				else:
					f1.write(f"\n\tfail\t{word_front_original}{word}{word_back_original}\n")
					# !!!fixme at this point send it back into battle with lwff as a failure

	f1.close()
	f2.close()


def x_word_sandhi_from_front_and_back():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}x-word sandhi from the front")
	print(f"{timeis()} {green}{line}")

	global printme
	printme = False

	global testme
	testme = False

	if testme == True:
		global unmatched2
		with open(f"output/pickle-2word-unmatched", "rb") as p:
			unmatched2 = pickle.load(p)

	with open("output/sandhi/processxfront.csv", "w") as f1:
		pass
	with open("output/sandhi/matches.csv", "a") as f2:
		pass

	global matchesx
	matchesx = []
	counter = 0
	
	if testme == True:
		data_set = unmatched2
		length = len(unmatched2)
	else:
		data_set = unmatched4
		length = len(unmatched4)

	for word in data_set:
		
		word_initial = word
		word_front = ""
		word_back = ""
		global tried
		tried = []
		comment = "start"
		rules_front = []
		rules_back = []
		
		if counter % 5 == 0:
			print(f"{timeis()} {counter}/{length} {word}")
		
		split_from_front_and_back(word_initial, word_front, word, word_back, comment, rules_front, rules_back)
		if printme:
			input(f"{timeis()} press enter to continue \n")
		counter += 1

	f1.close()
	f2.close()

	with open("output/sandhi/matchesx.csv", "w") as f:
		for word in matchesx:
			f.write(f"{word}\n")

	global unmatchedxfront
	unmatchedxfront = set(unmatched4) - set(matchesx)
	with open("output/sandhi/unmatchedxfront.csv", "w") as f:
		for word in unmatchedxfront:
			f.write(f"{word}\n")
	
	print(f"{timeis()} {green}x word matches {white}{len(matchesx)} {green}(including duplicates)")
	print(f"{timeis()} {green}x word unmatched from the front {white}{len(unmatchedxfront)}")


def summary():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}summary")
	print(f"{timeis()} {green}{line}")

	global unmatched_final
	# unmatched_final = set(unmatched_set) - set(matches2_api) - set(matches2) - set(matches3) - set(matches4)
	# unmatched_final = set(unmatched_set) - set(matches2) - set(matches3) - set(matches4)
	unmatched_final = set(unmatched_set) - set(matches2) - set(matches3) - set(matches4) - set(matchesx)


	with open("output/sandhi/unmatched.csv", "w") as f3:
		for item in unmatched_final:
			f3.write(f"{item}\n")

	perc_sandhi=(100 - ((len(unmatched_final) / len(unmatched_set))*100))
	perc_all=(100 - ((len(unmatched_final) / len(text_set))*100))

	print(f"{timeis()} {green}total unmatched {white}{len(unmatched_final)}")
	print(f"{timeis()} {green}sandhi unmatched {white}{len(unmatched_final)} / {len(unmatched_set)}")
	print(f"{timeis()} {green}sandhi matched {white}{perc_sandhi:.2f}%")
	print(f"{timeis()} {green}words in text unmatched {white}{len(unmatched_final)} / {len(text_set)}")
	print(f"{timeis()} {green}words in text matched {white}{perc_all:.2f}%")
	print(f"{timeis()} {green}{line}")
	
	with open("output/sandhi/stats.csv", "a") as f:
		f.write(f"{len(text_set)}\t{len(unmatched_set)}\t{len(matches2)}\t{len(unmatched2)}\t{len(matches3)}\t{len(unmatched3)}\t{len(matches4)}\t{len(unmatched4)}\t{len(matchesx)}\t{len(unmatchedxfront)}\t{perc_sandhi}\t{perc_all}\n")


def combine_matches_df():

	global matches_df

	print(f"{timeis()} {green}combining matches df's", end = " ")

	matches_df = pd.read_csv("output/sandhi/matches.csv", dtype=str, sep="\t")
	matches_df = matches_df.fillna("")

	# walk through matches dir

	# for root, dirs, files in os.walk("output/sandhi/matches"):
	# 	for file in files:
	# 		more_matches_df = pd.read_csv(f"output/sandhi/matches/{file}", dtype=str, sep="\t")
	# 		more_matches_df = more_matches_df.fillna("")
	# 		matches_df = pd.concat([matches_df, more_matches_df], ignore_index=True)
	
	# add splitcount and lettercount and count

	matches_df["splitcount"] = matches_df['split'].str.count('-')
	matches_df["lettercount"] = matches_df['split'].str.count('.')
	matches_df['count'] = matches_df.groupby('word')['word'].transform('size')

	# add difference ratio

	for row in range(len(matches_df)):
		original = matches_df.iloc[row, 0]
		split = matches_df.iloc[row, 1]
		# split = re.sub("-", "", split)
		matches_df.loc[row, 'ratio'] = SequenceMatcher(None, original, split).ratio()

	matches_df.sort_values(by=["splitcount", "ratio", "lettercount"], axis=0, ascending=[True, False, True], inplace=True, ignore_index=True)
	matches_df.drop_duplicates(subset=['word', 'split'], keep='first', inplace=True, ignore_index=True)
	matches_df.to_csv("output/sandhi/matches sorted.csv", sep="\t", index=None)

	print(f"{white}ok")
	
def make_sandhi_dict():

	print(f"{timeis()} {green}making sandhi dict")
	sandhi_dict = {}
	sandhi_dict_clean = {}

	with open("sandhi/sandhi.css", "r") as f:
		sandhi_css = f.read()

	matches_df_length = len(matches_df)

	for row in range(matches_df_length):  # matches_df_length
		word = matches_df.loc[row, 'word']

		if row % 1000 == 0:
			print(f"{timeis()} {white}{row}/{matches_df_length} {word}")

		if word not in sandhi_dict.keys():

			filter = matches_df['word'] == word
			word_df = matches_df[filter]
			word_df.reset_index(drop=True, inplace=True)

			length = len(word_df)
			if len(word_df) > 5:
				length = 5
			
			html_string = ""
			html_string_clean = ""
			html_string += sandhi_css
			html_string += f"<body><div class='sandhi'><p class='sandhi'>"

			for rowx in range(length):
				word = word_df.loc[rowx, 'word']
				split = word_df.loc[rowx, 'split']
				split = re.sub("-", " + ", split)
				split_words = split.split(" + ")
				rulez = str(word_df.loc[rowx, 'rules'])
				rulez = re.sub(" ", "", rulez)
				ratio = word_df.loc[rowx, 'ratio']

				# exclude negatives prefixed with a-
				# include double negatives
				
				neg_count = 0
				add = True

				for split_word in split_words:
					if split_word in neg_inflections_set:
						neg_count +=1
						if re.findall(f"(>| ){split_word[1:]}(<| )", html_string):
							add = False
						
				if add == True or \
				neg_count > 1:
					html_string += f"{split} <span class='sandhi'> ({rulez}) ({ratio: .4f})</span>"
					html_string_clean += split

					if rowx != length-1:
						html_string += f"<br>"
						html_string_clean += f"<br>"
					else:
						html_string += f"</p></div></body>"

			sandhi_dict.update({word: html_string})
			sandhi_dict_clean.update({word: html_string_clean})

	with open("output/sandhi dict", "wb") as pf:
		pickle.dump(sandhi_dict_clean, pf)

	sandhi_dict_df = pd.DataFrame(sandhi_dict.items())
	sandhi_dict_df.rename({0: "word", 1: "split"}, axis='columns', inplace=True)
	sandhi_dict_df.to_csv("output/sandhi/sandhi_dict_df.csv", index=None, sep="\t")
	

def make_golden_dict():

	print(f"{timeis()} {green}generating goldendict", end=" ")
	
	df = pd.read_csv("output/sandhi/sandhi_dict_df.csv", sep="\t", dtype=str)
	df = df.fillna("")
	df.insert(2, "definition_plain", "")
	df.insert(3, "synonyms", "")
	df.rename({"word": "word", "split": "definition_html"}, axis='columns', inplace=True)
	
	df.to_json("output/sandhi/matches.json", force_ascii=False, orient="records", indent=5)

	zip_path = Path("./output/sandhi/padavibhāga.zip")

	with open("output/sandhi/matches.json", "r") as gd_data:
		data_read = json.load(gd_data)

	def item_to_word(x):
		return DictEntry(
			word=x["word"],
			definition_html=x["definition_html"],
			definition_plain=x["definition_plain"],
			synonyms=x["synonyms"],)

	words = list(map(item_to_word, data_read))

	ifo = ifo_from_opts(
		{"bookname": "padavibhāga",
			"author": "Bodhirasa",
			"description": "",
			"website": "",}
			)

	export_words_as_stardict_zip(words, ifo, zip_path)	

	print(f"{white}ok")


def unzip_and_copy():

	print(f"{timeis()} {green}unipping and copying goldendict", end = " ")

	os.popen('unzip -o "output/sandhi/padavibhāga" -d "/home/bhikkhu/Documents/Golden Dict"')
	
	print(f"{white}ok")
	print(f"{timeis()} {green}{line}")


def value_counts():

	print(f"{timeis()} {green}saving value counts", end=" ")
	matches_df = pd.read_csv("output/sandhi/matches.csv", sep="\t")
	
	rules_string = ""

	for row in range(len(matches_df)):
		rulez = matches_df.loc[row, 'rules']
		rulez = re.sub("'", "", rulez)
		rulez = re.sub(r"\[|\]", "", rulez)
		rules_string = rules_string + rulez + ","

	rules_df = pd.DataFrame(rules_string.split(","))
	# print(rules_df)
	
	counts = rules_df.value_counts()
	counts.to_csv(f"output/sandhi/counts", sep="\t")

	print(f"{white}ok")

def word_counts():

	print(f"{timeis()} {green}saving word counts", end=" ") 

	df = pd.read_csv("output/sandhi/matches.csv", sep = "\t", dtype = str)
	df.drop_duplicates(subset=['word', 'split'], keep='first', inplace=True, ignore_index=True)

	masterlist = []

	for row in range(len(df)):
		split = df.loc[row, "split"]
		words = re.findall("[^ + |-]+", split)
		for word in words:
			masterlist.append(word)

	letters1 = []
	letters2 = []
	letters3 = []
	letters4 = []
	letters5 = []
	letters6 = []
	letters7 = []
	letters8 = []
	letters9 = []
	letters10plus = []

	for word in masterlist:
		if len(word) == 1:
			letters1.append(word)
		if len(word) == 2:
			letters2.append(word)
		if len(word) == 3:
			letters3.append(word)
		if len(word) == 4:
			letters4.append(word)
		if len(word) == 5:
			letters5.append(word)
		if len(word) == 6:
			letters6.append(word)
		if len(word) == 7:
			letters7.append(word)
		if len(word) == 8:
			letters8.append(word)
		if len(word) == 9:
			letters9.append(word)
		if len(word) >= 10:
			letters10plus.append(word)

	masterlist = sorted(masterlist)

	letters_df = pd.DataFrame(masterlist)
	letters_counts = letters_df.value_counts(sort=False)
	letters_counts.to_csv(f"output/sandhi/letters", sep="\t", header=None)
	letters_counts_sorted = letters_df.value_counts()
	letters_counts_sorted.to_csv(f"output/sandhi/letters sorted", sep="\t", header=None)
	
	letters1_df = pd.DataFrame(letters1)
	letters1_counts = letters1_df.value_counts(sort=False)
	letters1_counts.to_csv(f"output/sandhi/letters1", sep="\t", header=None)
	letters1_counts_sorted = letters1_df.value_counts()
	letters1_counts_sorted.to_csv(f"output/sandhi/letters1sorted", sep="\t", header=None)
	
	letters2_df = pd.DataFrame(letters2)
	letters2_counts = letters2_df.value_counts(sort=False)
	letters2_counts.to_csv(f"output/sandhi/letters2", sep="\t", header = None)
	letters2_counts_sorted = letters2_df.value_counts()
	letters2_counts_sorted.to_csv(f"output/sandhi/letters2sorted", sep="\t", header = None)

	letters3_df = pd.DataFrame(letters3)
	letters3_counts = letters3_df.value_counts(sort=False)
	letters3_counts.to_csv(f"output/sandhi/letters3", sep="\t", header=None)
	letters3_counts_sorted = letters3_df.value_counts()
	letters3_counts_sorted.to_csv(f"output/sandhi/letters3sorted", sep="\t", header=None)

	letters4_df = pd.DataFrame(letters4)
	letters4_counts = letters4_df.value_counts(sort=False)
	letters4_counts.to_csv(f"output/sandhi/letters4", sep="\t", header=None)
	letters4_counts_sorted = letters4_df.value_counts()
	letters4_counts_sorted.to_csv(f"output/sandhi/letters4sorted", sep="\t", header=None)

	letters5_df = pd.DataFrame(letters5)
	letters5_counts = letters5_df.value_counts(sort=False)
	letters5_counts.to_csv(f"output/sandhi/letters5", sep="\t", header=None)
	letters5_counts_sorted = letters5_df.value_counts()
	letters5_counts_sorted.to_csv(f"output/sandhi/letters5sorted", sep="\t", header=None)

	letters6_df = pd.DataFrame(letters6)
	letters6_counts = letters6_df.value_counts(sort=False)
	letters6_counts.to_csv(f"output/sandhi/letters6", sep="\t", header=None)
	letters6_counts_sorted = letters6_df.value_counts()
	letters6_counts_sorted.to_csv(f"output/sandhi/letters6sorted", sep="\t", header=None)

	letters7_df = pd.DataFrame(letters7)
	letters7_counts = letters7_df.value_counts(sort=False)
	letters7_counts.to_csv(f"output/sandhi/letters7", sep="\t", header=None)
	letters7_counts_sorted = letters7_df.value_counts()
	letters7_counts_sorted.to_csv(f"output/sandhi/letters7sorted", sep="\t", header=None)

	letters8_df = pd.DataFrame(letters8)
	letters8_counts = letters8_df.value_counts(sort=False)
	letters8_counts.to_csv(f"output/sandhi/letters8", sep="\t", header=None)
	letters8_counts_sorted = letters8_df.value_counts()
	letters8_counts_sorted.to_csv(f"output/sandhi/letters8sorted", sep="\t", header=None)

	letters9_df = pd.DataFrame(letters9)
	letters9_counts = letters9_df.value_counts(sort=False)
	letters9_counts.to_csv(f"output/sandhi/letters9", sep="\t", header=None)
	letters9_counts_sorted = letters9_df.value_counts()
	letters9_counts_sorted.to_csv(f"output/sandhi/letters9sorted", sep="\t", header=None)

	letters10plus_df = pd.DataFrame(letters10plus)
	letters10plus_counts = letters10plus_df.value_counts(sort=False)
	letters10plus_counts.to_csv(f"output/sandhi/letters10+", sep="\t", header=None)
	letters10plus_counts_sorted = letters10plus_df.value_counts()
	letters10plus_counts_sorted.to_csv(f"output/sandhi/letters10+sorted", sep="\t", header=None)

	print(f"{white}ok")


def test_me():

	print(f"{timeis()} {green}random test {white}10")
	print(f"{timeis()} {green}{green}{line}")
	for x in range(10):
		print(f"{timeis()} {white}{random.choice(list(unmatched_set))}")


tic()
make_text_set()
sc_text_set = make_sc_text_set()
make_spelling_mistakes_set()
make_variant_readings_set()
make_abbreviations_and_neg_set()
make_manual_corrections_set()
make_shortlist_set()
import_text_set()
make_all_inflections_set()
make_all_inflections_nfl_nll()
make_unmatched_set()
import_sandhi_rules()
remove_exceptions()
two_word_sandhi()
three_word_sandhi()
four_word_sandhi()
x_word_sandhi_from_front_and_back()
summary()
combine_matches_df()
make_sandhi_dict()
make_golden_dict()
unzip_and_copy()
value_counts()
word_counts()
test_me()
toc()