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

from modules import *
from timeis import timeis, blue, green, yellow, line, white, red
from typing import List
from pathlib import Path
from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry

warnings.filterwarnings("ignore", category=FutureWarning)

log = open("output/sandhi/log.txt", "a")

print(f"{timeis()} {line}")
print(f"{timeis()} {yellow}sandhi splitter")
print(f"{timeis()} {line}")

vowels = ["a", "ā", "i", "ī", "u", "ū", "o", "e"]

def make_text_set():

	print(f"{timeis()} {green}making text set")
	
	text_list = ["s0202m.mul.xml.txt", "s0202a.att.xml.txt"]
	# !!! change zip_path !!!

	# text_list = ["s0201m.mul.xml.txt", "s0201a.att.xml.txt", "s0202m.mul.xml.txt", "s0202a.att.xml.txt"]
	# text_list = ["s0512m.mul.xml.txt", "s0512a.att.xml.txt"]
	text_path = "../Cst4/txt/"
	text_string = ""
	
	for text in text_list:
		with open(f"{text_path}/{text}", "r") as f:
			text_string += f.read()

	text_string = clean_machine(text_string)
	text_set = set(sorted(text_string.split()))

	with open(f"output/set text", "wb") as p:
		pickle.dump(text_set, p)

def import_text_set():

	print(f"{timeis()} {green}importing text set", end=" ")
	
	global text_set
	with open(f"output/set text", "rb") as p:
		text_set = pickle.load(p)

	text_set.add("chedanaviniyogavinayakiriyālesantarakappataṇhādiṭṭhiasaṅkhyeyyakappamahākappādīsu")

	print(f"{white}{len(text_set)}")
	
def generate_inflected_forms_for_sandhi():

	global all_inflections_set
	all_inflections_set = []
	
	yn = input(f"{timeis()} {green}generate all inflected forms? (y/n){white} ")

	if yn == "y":
	
		dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
		dpd_df.fillna("", inplace=True)
		dpd_df_length = len(dpd_df)

		inflections_string = ""

		for row in range(dpd_df_length):  # dpd_df_length
			headword = dpd_df.loc[row, "Pāli1"]
			headword_clean = re.sub(r" \d*$", "", headword)
			stem = dpd_df.loc[row, "Stem"]
			if re.match("!.+", stem) != None:
				stem = "!"
			if stem == "*":
				stem = ""
			pattern = dpd_df.loc[row, "Pattern"]
			pos = dpd_df.loc[row, "POS"]

			if row % 5000 == 0:
				print(f"{timeis()} {row}/{len(dpd_df)}\t{headword}")

			exceptions_list = ["abbrev", "cs", "idiom", "letter", "prefix", "root", "sandhi", "suffix", "ve"]

			if pos not in exceptions_list:

				if stem == "-":
					inflections_string += headword_clean + " "
				
				elif stem == "!":
					inflections_string += headword_clean + " "

				else:
					
					try:
						df = pd.read_csv(f"output/patterns/{pattern}.csv", sep="\t", header=None)
						df.fillna("", inplace=True)
						df_rows = df.shape[0]
						df_columns = df.shape[1]

						for rows in range(1, df_rows):
							for columns in range(1, df_columns, 2):
								line = df.iloc[rows, columns]
								line = re.sub(r"(.+)", f"{stem}\\1", line)
								search_string = re.compile("\n", re.M)
								matches = re.sub(search_string, " ", line)
								inflections_string += matches + " "

					except:
						print(f"{timeis()} {red}error on: {headword}")
			
		all_inflections_set = sorted(set(inflections_string.split()))

		with open("output/set all inflections.csv", "w") as f:
			for item in all_inflections_set:
				f.write(f"{item}\n")
		
		with open("output/set all inflections", "wb") as p:
			pickle.dump(all_inflections_set, p)

	else:
		pass

def import_all_inflections_set():
	
	print(f"{timeis()} {green}importing all inflections set", end = " ")
	
	global all_inflections_set
	with open(f"output/set all inflections", "rb") as p:
		all_inflections_set = sorted(pickle.load(p))
	
	print(f"{white}{len(all_inflections_set)}")

def generate_all_inflections_string():

	print(f"{timeis()} {green}generating all inflections string", end=" ")

	global all_inflections_string
	all_inflections_string = ""
	all_inflections_string = ",".join(all_inflections_set) + ","
	print(f"ok")
	# print(all_inflections_string[:500])

def make_unmatched_set():

	print(f"{timeis()} {green}making unmatched set", end = " ")
	
	global unmatched_set
	unmatched_set = sorted(text_set - set(all_inflections_set))
	
	print(f"{white}{len(unmatched_set)}")

def import_sandhi_rules():

	print(f"{timeis()} {green}importing sandhi rules", end=" ")
	
	rules_df = pd.read_csv("sandhi rules.csv", sep="\t", dtype = str)
	rules_df.fillna("", inplace = True)
	
	print(f"{white}{len(rules_df)}")
	
	global rules
	rules = rules_df.to_dict('index')

	print(f"{timeis()} {green}testing sandhi rules for dupes", end = " ")

	dupes = rules_df[rules_df.duplicated(
		["chA", "chB", "ch1", "ch2"], keep=False)]

	if len(dupes) != 0:
		print(f"\n{timeis()} {red}duplicates found! please remove them and try again")
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
		print(f"\n{timeis()} {red}spaces found! please remove them and try again")
		print(f"{timeis()} {red}{line}")
		sys.exit()

	else:
		print(f"{white}ok")


def remove_exceptions():

	print(f"{timeis()} {green}removing exceptions", end=" ")

	exceptions_df = pd.read_csv("sandhi exceptions.csv", header = None)
	exceptions_set = set(exceptions_df[0].tolist())
	
	global unmatched_set
	unmatched_set = sorted(set(unmatched_set) - exceptions_set)
	
	global all_inflections_set
	all_inflections_set = set(all_inflections_set) - exceptions_set 
	
	print(f"{white}{len(exceptions_set)}")


def two_word_sandhi():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}two word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/process2.csv", "w")
	f2 = open("output/sandhi/matches.csv", "w")

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

			if \
			wordA in all_inflections_set and \
			wordB in all_inflections_set:
				f1.write(f"\t{wordA}\t{wordB}\t-\t-\tmatch\n")
				f2.write(f"{word}\t{wordA}-{wordB}\ttwo-word\t-\t-\t-\n")
				matches2.append(word)
			
			# bla* *lah
			
			for rule in rules:
				chA = rules[rule].get("chA")
				chB = rules[rule].get("chB")
				ch1 = rules[rule].get("ch1")
				ch2 = rules[rule].get("ch2")
				
				if \
				wordA_lastletter == chA and \
				wordB_firstletter == chB:
					word1 = wordA[:-1] + ch1
					word2 = ch2 + wordB[1:]

					if \
					word1 in all_inflections_set and \
					word2 in all_inflections_set:
						matches2.append(word)
						f1.write(f"\t{word1}\t{word2}\t{rule+2}\t-\tmatch\n")
						f2.write(f"{word}\t{word1}-{word2}\ttwo-word\t{rule+2}\t-\t-\n")
						
		counter += 1

	print(f"{timeis()} {green}two word matches {white}{len(matches2)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches2.csv", "w") as f:
		for word in matches2:
			f.write(f"{word}\n")

	global unmatched2
	unmatched2 = sorted(set(unmatched_set) - set(matches2))
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
					f2.write(f"{word}\t{wordA}-{wordB}-{wordC}\tthree-word\t-\t-\t-\n")

				# blah bla* *lah

				if wordA in all_inflections_set:

					for rule in rules:
						chA = rules[rule].get("chA")
						chB = rules[rule].get("chB")
						ch1 = rules[rule].get("ch1")
						ch2 = rules[rule].get("ch2")

						if \
						wordB_lastletter == chA and \
						wordC_firstletter == chB:
							word2 = wordB[:-1] + ch1
							word3 = ch2 + wordC[1:]

							if \
							wordA in all_inflections_set and \
							word2 in all_inflections_set and \
							word3 in all_inflections_set:
								matches3.append(word)
								f1.write(f"\t{wordA}\t{word2}\t{word3}\t-\t{rule+2}\tmatch\n")
								f2.write(f"{word}\t{wordA}-{word2}-{word3}\tthree-word\t-\t{rule+2}\t-\n")
				
				# bla* *lah blah

				if wordC in all_inflections_set:
					
					for rule in rules:
						chA = rules[rule].get("chA")
						chB = rules[rule].get("chB")
						ch1 = rules[rule].get("ch1")
						ch2 = rules[rule].get("ch2")

						if \
						wordA_lastletter == chA and \
						wordB_firstletter == chB:
							word1 = wordA[:-1] + ch1
							word2 = ch2 + wordB[1:]

							if \
							word1 in all_inflections_set and \
							word2 in all_inflections_set and \
							wordC in all_inflections_set:
								matches3.append(word)
								f1.write(f"\t{word1}\t{word2}\t{wordC}\t{rule+2}\t-\tmatch\n")
								f2.write(f"{word}\t{word1}-{word2}-{wordC}\tthree-word\t{rule+2}\t-\t-\n")

				# bla* *la* *lah
				
				for rulex in rules:
					chAx = rules[rulex].get("chA")
					chBx = rules[rulex].get("chB")
					ch1x = rules[rulex].get("ch1")
					ch2x = rules[rulex].get("ch2")

					if \
					wordA_lastletter == chAx and \
					wordB_firstletter == chBx:
						word1 = wordA[:-1] + ch1x
						word2 = ch2x + wordB[1:]
					
						for ruley in rules:
							chAy = rules[ruley].get("chA")
							chBy = rules[ruley].get("chB")
							ch1y = rules[ruley].get("ch1")
							ch2y = rules[ruley].get("ch2")

							if \
							wordB_lastletter == chAy and \
							wordC_firstletter == chBy:
								word2 = (ch2x + wordB[1:])[:-1] + ch1y
								word3 = ch2y + wordC[1:]

								if \
								word1 in all_inflections_set and \
								word2 in all_inflections_set and \
								word3 in all_inflections_set:
									matches3.append(word)
									f1.write(f"\t{word1}\t{word2}\t{word3}\t{rulex+2}\t{ruley+2}\tmatch\n")
									f2.write(f"{word}\t{word1}-{word2}-{word3}\tthree-word\t{rulex+2}\t{ruley+2}\t-\n")
								
		counter += 1

	print(f"{timeis()} {green}three word matches {white}{len(matches3)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches3.csv", "w") as f:
		for word in matches3:
			f.write(f"{word}\n")

	global unmatched3
	unmatched3 = sorted(set(unmatched2) - set(matches3))
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

		if counter % 50 == 0:
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

					if \
					wordA in all_inflections_set and \
					wordB in all_inflections_set and \
					wordC in all_inflections_set and \
					wordD in all_inflections_set:
						matches4.append(word)
						f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\t-\t-\t-\tmatch\n")
						f2.write(f"{word}\t{wordA}-{wordB}-{wordC}-{wordD}\tfour-word\t-\t-\t-\n")

					# blah blah bla* *lah

					if \
					wordA in all_inflections_set and \
					wordB in all_inflections_set:
							
						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if \
							wordC_lastletter == chA and \
							wordD_firstletter == chB:
								word3 = wordC[:-1] + ch1
								word4 = ch2 + wordD[1:]

								if \
								word3 in all_inflections_set and \
								word4 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{wordA}\t{wordB}\t{word3}\t{word4}\t-\t-\t{rule+2}\tmatch\n")
									f2.write(f"{word}\t{wordA}-{wordB}-{word3}-{word4}\tfour-word\t-\t-\t{rule+2}\n")

					# bla* *lah blah blah

					if \
					wordC in all_inflections_set and \
					wordD in all_inflections_set:

						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if \
							wordA_lastletter == chA and \
							wordB_firstletter == chB:
								word1 = wordA[:-1] + ch1
								word2 = ch2 + wordB[1:]

								if \
								word1 in all_inflections_set and \
								word2 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{word1}\t{word2}\t{wordC}\t{wordD}\t{rule+2}-\t-\t\tmatch\n")
									f2.write(f"{word}\t{word1}-{word2}-{wordC}-{wordD}\tfour-word\t{rule+2}\t-\t-\n")

					# blah bla* *lah blah

					if \
					wordA in all_inflections_set and \
					wordD in all_inflections_set:

						for rule in rules:
							chA = rules[rule].get("chA")
							chB = rules[rule].get("chB")
							ch1 = rules[rule].get("ch1")
							ch2 = rules[rule].get("ch2")

							if \
							wordB_lastletter == chA and \
							wordC_firstletter == chB:
								word2 = wordB[:-1] + ch1
								word3 = ch2 + wordC[1:]

								if \
								word2 in all_inflections_set and \
								word3 in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{wordA}\t{word2}\t{word3}\t{wordD}\t-\t{rule+2}\t-\tmatch\n")
									f2.write(f"{word}\t{wordA}-{word2}-{word3}-{wordD}\tfour-word\t-\t{rule+2}\t-\n")
					
					# blah bla* *la* *lah

					if wordA in all_inflections_set:

						for rulex in rules:
							chAx = rules[rulex].get("chA")
							chBx = rules[rulex].get("chB")
							ch1x = rules[rulex].get("ch1")
							ch2x = rules[rulex].get("ch2")

							if \
							wordB_lastletter == chAx and \
							wordC_firstletter == chBx:
								word2 = wordB[:-1] + ch1x
								word3 = ch2x + wordC[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if \
									wordC_lastletter == chAy and \
									wordD_firstletter == chBy:
										word3 = (ch2x + wordC[1:])[:-1] + ch1y
										word4 = ch2y + wordD[1:]

										if \
										word2 in all_inflections_set and \
										word3 in all_inflections_set and \
										word4 in all_inflections_set:
											matches4.append(word)
											f1.write(f"\t{wordA}\t{word2}\t{word3}\t{word4}\t-\t{rulex+2}\t{ruley+2}\tmatch\n")
											f2.write(f"{word}\t{wordA}-{word2}-{word3}-{word4}\tfour-word\t-\t{rulex+2}\t{ruley+2}\n")

					# bla* *la* *lah blah

					if wordD in all_inflections_set:

						for rulex in rules:
							chAx = rules[rulex].get("chA")
							chBx = rules[rulex].get("chB")
							ch1x = rules[rulex].get("ch1")
							ch2x = rules[rulex].get("ch2")

							if \
							wordA_lastletter == chAx and \
							wordB_firstletter == chBx:
								word1 = wordA[:-1] + ch1x
								word2 = ch2x + wordB[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if \
									wordB_lastletter == chAy and \
									wordC_firstletter == chBy:
										word2 = (ch2x + wordB[1:])[:-1] + ch1y
										word3 = ch2y + wordC[1:]

										if \
										word1 in all_inflections_set and \
										word2 in all_inflections_set and \
										word3 in all_inflections_set:
											matches4.append(word)
											f1.write(f"\t{word1}\t{word2}\t{word3}\t{wordD}\t{rulex+2}\t{ruley+2}\t-\tmatch\n")
											f2.write(f"{word}\t{word1}-{word2}-{word3}-{wordD}\tfour-word\t{rulex+2}\t{ruley+2}\t-\n")

					# bla* *lah bla* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if \
                        wordA_lastletter == chAx and \
                        wordB_firstletter == chBx:
							word1 = wordA[:-1] + ch1x
							word2 = ch2x + wordB[1:]

							for ruley in rules:
								chAy = rules[ruley].get("chA")
								chBy = rules[ruley].get("chB")
								ch1y = rules[ruley].get("ch1")
								ch2y = rules[ruley].get("ch2")

								if \
								wordC_lastletter == chAy and \
								wordD_firstletter == chBy:
									word3 = wordC[:-1] + ch1y
									word4 = ch2y + wordD[1:]

									if \
									word1 in all_inflections_set and \
									word2 in all_inflections_set and \
									word3 in all_inflections_set and \
									word4 in all_inflections_set:
										matches4.append(word)
										f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t-\t{ruley+2}\tmatch\n")
										f2.write(f"{word}\t{word1}-{word2}-{word3}-{word4}\tfour-word\t{rulex+2}\t-\t{ruley+2}\n")

					# bla* *la* *la* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if \
						wordA_lastletter == chAx and \
						wordB_firstletter == chBx:
							word1 = wordA[:-1] + ch1x
							word2 = ch2x + wordB[1:]

							for ruley in rules:
								chAy = rules[ruley].get("chA")
								chBy = rules[ruley].get("chB")
								ch1y = rules[ruley].get("ch1")
								ch2y = rules[ruley].get("ch2")

								if \
								wordB_lastletter == chAy and \
								wordC_firstletter == chBy:
									word2 = (ch2x + wordB[1:])[:-1] + ch1y
									word3 = ch2y + wordC[1:]

									for rulez in rules:
										chAz = rules[rulez].get("chA")
										chBz = rules[rulez].get("chB")
										ch1z = rules[rulez].get("ch1")
										ch2z = rules[rulez].get("ch2")

										if \
										wordC_lastletter == chAz and \
										wordD_firstletter == chBz:
											word3 =(ch2y + wordC[1:])[:-1] + ch1z
											word4 = ch2z + wordD[1:]

											if \
											word1 in all_inflections_set and \
											word2 in all_inflections_set and \
											word3 in all_inflections_set and \
											word4 in all_inflections_set:
												matches4.append(word)
												f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t{ruley+2}\t{rulez+2}\tmatch\n")
												f2.write(f"{word}\t{word1}-{word2}-{word3}-{word4}\tfour-word\t{rulex+2}\t{ruley+2}\t{rulez+2}\n")

		counter += 1

	print(f"{timeis()} {green}four word matches {white}{len(matches4)} {green}(including duplicates)")

	f1.close()
	f2.close()

	with open ("output/sandhi/matches4.csv", "w") as f:
		for word in matches4:
			f.write(f"{word}\n")

	global unmatched4
	unmatched4 = set(sorted(unmatched3)) - set(matches4)
	with open("output/sandhi/unmatched4.csv", "w") as f:
		for word in unmatched4:
			f.write(f"{word}\n")
			
	print(f"{timeis()} {green}four word unmatched {white}{len(unmatched4)}")


def splitter_old(word_initial, word, length, recursions, counter, match_count):

	if counter-1 % 100 == 0:
		print(f"{timeis()} {counter}\\{length}\t{word_initial}")

	f1 = open("output/sandhi/processx.csv", "a")
	f2 = open("output/sandhi/matchesx.csv", "a")

	recursions += 1
	word_in_process = re.sub("-.+$", "", word)
	word_end = re.sub(f"^{word_in_process}", "", word)

	f1.write(f"{counter}\\{length}r{recursions}\t{word_in_process} {word_end} ")
	if word_in_process in all_inflections_set:
		match_count += 1
		splits = len(re.findall("-", word))
		f1.write(f"match!\n")
		f2.write(f"{word_initial}\t{word}\t{splits}\n")
		pass
	else:
		f1.write(f"\n")

	test = re.findall("(pi|ca|ce|va|ti)$", word_in_process)
	if test != [] and \
	match_count < 10 and \
	recursions < 2:
		# f1.write(f"\tends in api ca ce eva iti\n")
		wordA = word_in_process[:-2]
		wordA_lastletter = wordA[-1]
		wordB = word_in_process[-2:]
		wordB_firstletter = wordB[0]
		# f1.write(f"{wordA} {wordB}\n")

		for rule in rules:
			chA = rules[rule].get("chA")
			chB = rules[rule].get("chB")
			ch1 = rules[rule].get("ch1")
			ch2 = rules[rule].get("ch2")

			if wordA_lastletter == chA and \
            wordB_firstletter == chB:

				word1 = wordA[:-1] + ch1
				word2 = ch2 + wordB[1:]
				# f1.write(f"\t{word1} {word2}\n")

				test = re.findall(f"{word1[-3:]} ", all_inflections_string)
				
				if \
				len(test) != 0 and \
				len(word2) > 2 and \
				word2 in all_inflections_set:
					# f1.write(f"test {test[0]}\n")
					word_to_recurse = f"{word1}-{word2}{word_end}"
					splitter_old(word_initial, word_to_recurse, length,
					             recursions, counter, match_count)

	
	for x in range(len(word_in_process)-1):
		wordA = word_in_process[:1+x]
		wordB = word_in_process[1+x:]
		wordA_lastletter = wordA[-1]
		wordB_firstletter = wordB[0]
		# f1.write(f"\t{wordA}-{wordB}  {word_end}\n")

		test = re.findall(f"{wordA[-2:-1]}. ", all_inflections_string)

		if \
		match_count < 10 and \
		len(test) != 0 and \
		len(wordB) > 2 and \
        wordB in all_inflections_set and\
		len(wordA) > 3:
			word_to_recurse = f"{wordA}-{wordB}{word_end}"
			splitter_old(word_initial, word_to_recurse, length,
			             recursions, counter, match_count)
		

		if match_count < 10:
			for rule in rules:
				chA = rules[rule].get("chA")
				chB = rules[rule].get("chB")
				ch1 = rules[rule].get("ch1")
				ch2 = rules[rule].get("ch2")

				if \
				wordA_lastletter == chA and \
				wordB_firstletter == chB:

					word1 = wordA[:-1] + ch1
					word2 = ch2 + wordB[1:]
					# f1.write(f"\t\t{word1} {word2}\n")

					test = re.findall(f"{word1[-3:] } ", all_inflections_string)

					if \
					len(test) != 0 and \
					len(word2) > 2 and \
					word2 in all_inflections_set:
						# f1.write(f"pass\t\t{word1} {word2}\n")
						word_to_recurse = f"{word1}-{word2}{word_end}"
						splitter_old(word_initial, word_to_recurse, length,
						         recursions, counter, match_count)


def x_word_sandhi_old():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}x word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/processx.csv", "w")
	f2 = open("output/sandhi/matchesx.csv", "w")

	counter=0
	df = pd.read_csv("output/sandhi/unmatched4.csv", header = None)
	length = len(df)
	for row in range(100):  # len(df)
		word = df.iloc[row, 0]
		word_initial = word
		recursions = 0
		counter += 1
		match_count = 0
		splitter_old(word_initial, word, length, recursions, counter, match_count)


def split_from_back(word_initial, word, word_back):
	lwfb = ""
	f1 = open("output/sandhi/processx.csv", "a")
	f2 = open("output/sandhi/matches.csv", "a")
	f1.write(f"{word_initial}\t{word}\t{word_back}\n")

	# is word a match?

	if word in all_inflections_set:
		matchesxback.append(word_initial)
		f1.write(f"match!\t{word_initial}\t{word}{word_back}\n")
		f2.write(f"{word_initial}\t{word}{word_back}\tx-wordback\n")
	
	else:
	
		# does word end in api ca eva iti?

		apicaevaiti = re.findall("(pi|va|ti)$", word)
		if apicaevaiti != []:

			f1.write(f"\t{apicaevaiti}\n")

			for rule in rules:
				chA = rules[rule].get("chA")
				chB = rules[rule].get("chB")
				ch1 = rules[rule].get("ch1")
				ch2 = rules[rule].get("ch2")

				wordA = word[:-2]
				wordB = word[-2:]
				try:
					wordA_lastletter = wordA[-1]
				except:
					wordA_lastletter = wordA

				wordB_firstletter = wordB[0]
				# f1.write(f"ab\t{wordA} {wordB}\t{rule}\n")
				# f1.write(f"ab\t{wordA_lastletter} {wordB_firstletter}\n")

				if \
				wordA_lastletter == chA and \
				wordB_firstletter == chB:
					word1 = wordA[:-1] + ch1
					word2 = ch2 + wordB[1:]
					# f1.write(f"if\t{word1}\t{word2}\n")

					if \
					word2 == "api" or \
					word2 == "ca" or \
					word2 == "eva" or \
					word2 == "iti":
						word_back = "-" + word2 + word_back 
						word_to_recurse = word1
						# f1.write(f"fin\t{word}\t{word_back}\n")
						split_from_back(word_initial, word_to_recurse, word_back)

		if apicaevaiti == []:

			# find longest word from the back

			for x in range(len(word)-3):
				wordA = word[:2+x]
				wordB = word[2+x:]
				# f1.write(f"split\t{wordA} {wordB}\n")
				
				if wordB in all_inflections_set and \
				len(wordB) > 1 and \
				len(wordB) > len(lwfb):
					lwfb = wordB

			f1.write(f"\tlwfb\t{lwfb}\n")

			wordA = re.sub(f"{lwfb}$", "", word)
			wordB = lwfb
			wordA_lastletter = wordA[-1]
			try:
				wordB_firstletter = wordB[0]
			except:
				wordB_firstletter = ""
			# f1.write(f"{wordA}\t{wordB}\n")

			test = re.findall(f"{wordA[-3:]},", all_inflections_string)
			f1.write(f"\t{sorted(set(test))}\n")

			# split without rules
			
			if \
			len(lwfb) > 0 and \
			test != []:
				word_to_recurse = re.sub(f"{lwfb}$", "", word)
				word_back = f"-{lwfb}{word_back}" 
				f1.write(f"\tfin\t{word}\t{word_back}\n")
				split_from_back(word_initial, word_to_recurse, word_back)

			# split with rules

			# fixme put another test here to check if xx. in all inflections
			
			if \
			len(lwfb) > 0 and \
			test == []:

				for rule in rules:
					chA = rules[rule].get("chA")
					chB = rules[rule].get("chB")
					ch1 = rules[rule].get("ch1")
					ch2 = rules[rule].get("ch2")

					if \
					wordA_lastletter == chA and \
					wordB_firstletter == chB:
						word1 = wordA[:-1] + ch1
						word2 = ch2 + wordB[1:]
						f1.write(f"\trules\t{word1}\t{word2}\n")
						
						if word2 in all_inflections_set:
							test = re.findall(f"{word1[-4:]},", all_inflections_string)
							f1.write(f"\ttestword1\t{test[:5]}\n")

							if test != []:
								word_to_recurse = word1
								word_back = "-" + word2 + word_back
								f1.write(f"fin\t{word_to_recurse}\t{word_back}\n")
								split_from_back(word_initial, word_to_recurse, word_back)
		else:
			f1.write(f"\tfail\t{word}{word_back}\n")	

	f1.close()
	f2.close()

def x_word_sandhi_from_back():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}x-word sandhi from the back")
	print(f"{timeis()} {green}{line}")

	with open ("output/sandhi/processxback.csv", "w") as f1:
		pass
	with open("output/sandhi/matches.csv", "a") as f2:
		pass

	global matchesxback
	matchesxback = []
	counter = 0
	length = len(unmatched3)
	for word in unmatched3:
		word_initial = word
		word_back = ""
		split_from_back(word_initial, word, word_back)
		if counter % 100 == 0:
			print(f"{timeis()} {counter}/{length}\t{word}")
		counter += 1

	f1.close()
	f2.close()

	with open("output/sandhi/matchesxback.csv", "w") as f:
		for word in matchesxback:
			f.write(f"{word}\n")

	global unmatchedxback
	unmatchedxback = set(sorted(unmatched3)) - set(matchesxback)
	with open("output/sandhi/unmatchedx.csv", "w") as f:
		for word in unmatchedxback:
			f.write(f"{word}\n")

	print(f"{timeis()} {green}x word unmatched from the back {white}{len(unmatchedxback)}")


def split_from_front_and_back(word_initial, word_front, word, word_back, tried, comment):


	f1 = open("output/sandhi/processxfront.csv", "a")
	f2 = open("output/sandhi/matches.csv", "a")
	f1.write(f"{word_initial}\t{word_front}\t{word}\t({comment})\n")
	# print(f"{timeis()} word: {yellow}{word_initial} : {green}{word_front}{blue}{word}{green}{word_back} {white}({comment})")

	word_front_original = word_front
	word_back_original = word_back
	lwff_clean = ""
	lwff_fuzzy = ""
	comment = ""

	# is word a match?

	if word in all_inflections_set:
		matchesxfront.append(word_initial)
		f1.write(f"\tmatch!\t{word_initial}\t{word_front}{word}{word_back}\n")
		f2.write(f"{word_initial}\t{word_front}{word}{word_back}\tx-wordfront\n")
		# print(f"{timeis()} {red}match! {yellow}{word_front}{blue}{word}{green}{word_back}")

	else:

		# # does word end in api ca eva iti?

		# apicaevaiti = re.findall("(pi|va|ti)$", word)

		# if apicaevaiti != []:

		# 	f1.write(f"\t{apicaevaiti}\n")

		# 	for rule in rules:
		# 		chA = rules[rule].get("chA")
		# 		chB = rules[rule].get("chB")
		# 		ch1 = rules[rule].get("ch1")
		# 		ch2 = rules[rule].get("ch2")

		# 		wordA = word[:-2]
		# 		wordB = word[-2:]
		# 		try:
		# 			wordA_lastletter = wordA[-1]
		# 		except:
		# 			wordA_lastletter = wordA
		# 		wordB_firstletter = wordB[0]

		# 		if \
		# 		wordA_lastletter == chA and \
		# 		wordB_firstletter == chB:
		# 			word1 = wordA[:-1] + ch1
		# 			word2 = ch2 + wordB[1:]
		# 			f1.write(f"\tapicaeveiti\t{word1}\t{word2}\n")

		# 			if \
		# 			word2 == "api" or \
		# 			word2 == "ca" or \
		# 			word2 == "eva" or \
		# 			word2 == "iti":
		# 				word_to_recurse = word1
		# 				word_back_to_recurse = f"-{word2}{word_back_original}"
		# 				# word_front = f"{word_front_original}"
		# 				tried.append(f"{word_front_original}{word1}-{word2}")
		# 				f1.write(f"\tapicaeveiti fin:\t{word_front}\t{word_to_recurse}\t{word_back}\n")
		# 				# print(f"{timeis()} fuzzy: {green}{word_front}{blue}{word_to_recurse}\n")
		# 				comment = "api ca eva iti"
		# 				split_from_front_and_back(word_initial, word_front, word_to_recurse, word_back_to_recurse, tried, comment)
	

		# if apicaevaiti == []:
	
		# find longest fuzzy word from the front
		
		def find_longest_word_fuzzy(word):

			lwff_fuzzy = []
			lwfb_fuzzy = []

			for x in range(len(word)-3):
				wordA = word[:2+x]
				wordB = word[2+x:]

				fuzzy_searchA = re.findall(f",{wordA[:-1]}.,", all_inflections_string)

				if \
				fuzzy_searchA != [] and \
				len(wordA) > 0 and \
				len(fuzzy_searchA[0]) > len(lwff_fuzzy):
					lwff_fuzzy = [wordA] + lwff_fuzzy

				fuzzy_searchB = re.findall(f",.{wordB[1:]},", all_inflections_string)
				# print(f"{timeis()} fuzzysearchB\t{fuzzy_searchB}")

				if \
				fuzzy_searchB != [] and \
				len(wordB) > 0 and \
				len(fuzzy_searchB[0]) > len(lwfb_fuzzy):
					lwfb_fuzzy = [wordB] + lwfb_fuzzy
				lwfb_fuzzy = sorted(lwfb_fuzzy, key=len, reverse=True)

			
			f1.write(f"\tlwff_fuzzy\t{lwff_fuzzy}\n")
			f1.write(f"\tlwfb_fuzzy\t{lwfb_fuzzy}\n")
			# print(f"{timeis()} lwff-fuzzy\t{lwff_fuzzy}")
			# print(f"{timeis()} lwfb-fuzzy\t{lwfb_fuzzy}")

			return [lwff_fuzzy, lwfb_fuzzy]
		
		lwff_lwfb = find_longest_word_fuzzy(word)
		lwff_fuzzy = lwff_lwfb[0]
		lwfb_fuzzy = lwff_lwfb[1]
		# print(f"{timeis()} lwff_fuzzy\t{lwff_fuzzy}")
		# print(f"{timeis()} lwfb_fuzzy\t{lwfb_fuzzy}")

		# split fuzzy, run rules and recurse

		if len(lwff_fuzzy) != 0:

			if (lwff_fuzzy[0][-1]) in vowels:
				wordA_fuzzy = (lwff_fuzzy[0][:-1])
			else:
				wordA_fuzzy = (lwff_fuzzy[0])
			
			wordB_fuzzy = re.sub(f"^{wordA_fuzzy}", "", word)
			try:
				wordA_lastletter = wordA_fuzzy[-1]
			except:
				wordA_lastletter = ""
			try:
				wordB_firstletter = wordB_fuzzy[0]
			except:
				wordB_firstletter = ""
			# print(f"{timeis()} {wordA_lastletter}-{wordB_firstletter}")

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
					f1.write(f"\tfuzzy words:\t{word1}-{word2}\n")
					# print(f"{timeis()} fuzzy words: {green}{word1}-{blue}{word2}")

					if word1 in all_inflections_set:
						test = re.findall(f",{word2[:2]}", all_inflections_string)
						f1.write(f"\ttestword2\t{test[:5]}\n")
						# print(f"{timeis()} testword2\t{test[:5]}")

						if \
						test != [] and \
						word not in tried:
							word_to_recurse = word2
							tried.append(f"{word_front_original}{word1}-{word2}{word_back}")
							word_front_to_recurse = f"{word_front_original}{word1}-"
							f1.write(f"\tfuzzy fin:\t{word_front}\t{word_to_recurse}\t{word_back}\n")
							# print(f"{timeis()} fuzzy: {green}{word_front}{blue}{word_to_recurse}\t{word_back}\n")
							comment = "fuzzy"
							split_from_front_and_back(word_initial, word_front_to_recurse, word_to_recurse, word_back, tried, comment)

	# find longest clean word from the front

		def find_longest_word_clean(word):

			lwff_clean = []
			lwfb_clean = []

			for x in range(len(word)-3):
				wordA = word[:2+x]
				wordB = word[2+x:]

				clean_searchA = wordA in all_inflections_set

				if \
				clean_searchA != False and \
				len(wordA) > 0 and \
				len(wordA) > len(lwff_clean):
					lwff_clean = [wordA] + lwff_clean

				clean_searchB = wordB in all_inflections_set

				if \
				clean_searchB != False and \
				len(wordB) > 0 and \
				len(wordB) > len(lwfb_clean):
					lwfb_clean = [wordB] + lwfb_clean
				lwfb_clean = sorted(lwfb_clean, key=len, reverse=True)


			f1.write(f"\tlwff-clean\t{lwff_clean}\n")
			# print(f"{timeis()} lwff-clean\t{lwff_clean}")
			f1.write(f"\tlwfb-clean\t{lwfb_clean}\n")
			# print(f"{timeis()} lwfb-clean\t{lwfb_clean}")

			return [lwff_clean, lwfb_clean]

		lwfb_lwff = find_longest_word_clean(word)
		lwff_clean = lwfb_lwff[0]
		lwfb_clean = lwfb_lwff[1]

		# split clean, run rules and recurse

		# lwff

		if len(lwff_clean) > 0:

			wordA = lwff_clean[0]
			wordB = re.sub(f"^{wordA}", "", word)
			f1.write(f"\tclean words from front:\t{wordA}\t{wordB}\n")
			# print(f"{timeis()} clean words from front: {green}{wordA}-{blue}{wordB}")

			test = re.findall(f",{wordB[:2]}", all_inflections_string)
			f1.write(f"\ttestB\t{sorted(set(test))}\n")
			# print(f"{timeis()} testB\t{sorted(set(test))}")

			if \
			test != [] and \
			wordA not in tried:

				word_to_recurse = re.sub(f"^{wordA}", "", word)
				tried.append(f"{word_front_original}{wordA}-{word_to_recurse}{word_back}")
				word_front_to_recurse = f"{word_front_original}{wordA}-"
				f1.write(f"\tcleanfin\t{word_front}\t{word_to_recurse}\t{word_back}\n")
				# print(f"{timeis()} clean front: {green}{word_front}{blue}{word_to_recurse}\t{word_back}\n")
				comment = "lwff clean"
				split_from_front_and_back(word_initial, word_front_to_recurse, word_to_recurse, word_back, tried, comment)

		# lwfb

		if len(lwfb_clean) > 0:

			wordB = lwfb_clean[0]
			wordA = re.sub(f"{wordB}$", "", word)
			f1.write(f"\tclean words from back:\t{wordA}\t{wordB}\n")
			# print(f"{timeis()} clean words from back: {green}{wordA}-{blue}{wordB}")

			test = re.findall(f"{wordA[-2:]},", all_inflections_string)
			f1.write(f"\ttestA\t{sorted(set(test))}\n")
			# print(f"{timeis()} testA\t{sorted(set(test))}")

			if \
			test != [] and \
			wordB not in tried:

				word_front = word_front_original
				word_to_recurse = wordA
				word_back_to_recurse = f"-{wordB}{word_back_original}"
				tried.append(f"{word_front}{word_to_recurse}{word_back}")
				f1.write(f"\tcleanfin\t{word_front}\t{word_to_recurse}\t{word_back}\n")
				# print(f"{timeis()} clean back: {green}{word_front}{blue}{word_to_recurse}\t{word_back}\n")
				comment = "lwfb clean"
				split_from_front_and_back(word_initial, word_front, word_to_recurse,
									word_back_to_recurse, tried, comment)
	
		else:
			f1.write(f"\tfail\t{word_front}{word}\n")
			# !!!fixme at this point send it back into battle with lwff as a failure

	f1.close()
	f2.close()

def x_word_sandhi_from_front_and_back():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}x-word sandhi from the front")
	print(f"{timeis()} {green}{line}")

	# global unmatched2
	# with open(f"output/pickle-2word-unmatched", "rb") as p:
	# 	unmatched2 = pickle.load(p)

	# global all_inflections_string
	# with open(f"output/pickle-all-inflections-string", "rb") as p:
	# 	all_inflections_string = pickle.load(p)

	with open("output/sandhi/processxfront.csv", "w") as f1:
		pass
	with open("output/sandhi/matches.csv", "a") as f2:
		pass

	global matchesxfront
	matchesxfront = []
	counter = 0
	length = len(unmatched4)
	
	for word in unmatched4:
		
		word_initial = word
		word_front = ""
		word_back = ""
		tried = []
		comment = "start"
		
		if counter % 100 == 0:
			print(f"{timeis()} {counter}/{length} {word}")
		
		split_from_front_and_back(word_initial, word_front, word, word_back, tried, comment)
		# input(f"{timeis()} press enter to continue \n")
		counter += 1

	f1.close()
	f2.close()

	with open("output/sandhi/matchesxfront.csv", "w") as f:
		for word in matchesxfront:
			f.write(f"{word}\n")

	global unmatchedxfront
	unmatchedxfront = sorted(set(unmatched4) - set(matchesxfront))
	with open("output/sandhi/unmatchedxfront.csv", "w") as f:
		for word in unmatchedxfront:
			f.write(f"{word}\n")

	print(f"{timeis()} {green}x word unmatched from the front {white}{len(unmatchedxfront)}")


def summary():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}summary")
	print(f"{timeis()} {green}{line}")

	global unmatched_final
	# unmatched_final = sorted(set(unmatched_set) - set(matches2_api) - set(matches2) - set(matches3) - set(matches4))
	# unmatched_final = sorted(set(unmatched_set) - set(matches2) - set(matches3) - set(matches4))
	unmatched_final = sorted(set(unmatched_set) - set(matches2) - set(matches3) - set(matches4) - set(matchesxfront))


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
		f.write(f"{len(text_set)}\t{len(unmatched_set)}\t{len(matches2)}\t{len(unmatched2)}\t{len(matches3)}\t{len(unmatched3)}\t{len(matches4)}\t{len(unmatched4)}\t{len(matchesxfront)}\t{len(unmatchedxfront)}\t{perc_sandhi}\t{perc_all}\n")

def make_sandhi_dict():

	print(f"{timeis()} {green}saving matches_df", end=" ")

	matches_df = pd.read_csv("output/sandhi/matches.csv", dtype=str, sep="\t", header=None)
	matches_df = matches_df.fillna("")
	matches_df.drop([2, 3], inplace=True, axis=1)
	sandhi_dict = {}

	for row in range(len(matches_df)):
		sandhi = matches_df.iloc[row, 0]
		construction = matches_df.iloc[row, 1]

		if sandhi not in sandhi_dict.keys():
			sandhi_dict.update({sandhi: {construction}})

		if sandhi in sandhi_dict.keys():
			sandhi_dict[sandhi].add(construction)

	matches_df = pd.DataFrame(sandhi_dict.items())
	matches_df.rename({0: "sandhi", 1: "construction"}, axis='columns', inplace=True)
	matches_df.to_csv("output/sandhi/matches_df.csv", index=None, sep="\t")
	
	print(f"{white}ok")

def make_golden_dict():

	print(f"{timeis()} {green}generating goldendict", end=" ")
	
	df = pd.read_csv("output/sandhi/matches_df.csv", sep="\t", dtype=str)
	df = df.fillna("")

	df["construction"] = df["construction"].str.replace(r"{|}", "")
	df["construction"] = df["construction"].str.replace("'", "")
	df["construction"] = df["construction"].str.replace(", ", "<br>")

	df.insert(2, "definition_plain", "")
	df.insert(3, "synonyms", "")
	df.rename({"sandhi": "word", "construction": "definition_html"}, axis='columns', inplace=True)
	
	df.to_json("output/sandhi/matches.json",
	           force_ascii=False, orient="records", indent=5)

	zip_path = Path("./output/sandhi/DPD SSS MN2 mūla.zip")
	# change bookname
	# change unzip

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
		{"bookname": "DPD SSS MN2 mūla",
			"author": "Bodhirasa",
			"description": "",
			"website": "",}
			)

	export_words_as_stardict_zip(words, ifo, zip_path)	

	print(f"{white}ok")

def unzip_and_copy():

	print(f"{timeis()} {green}unipping and copying goldendict", end = " ")

	os.popen('unzip -o "output/sandhi/DPD SSS MN2 mūla" -d "/home/bhikkhu/Documents/Golden Dict"')
	
	print(f"{white}ok")
	print(f"{timeis()} {green}{line}")

def value_counts():

	print(f"{timeis()} {green}saving value counts", end=" ")
	df = pd.read_csv(
		"/home/bhikkhu/Bodhirasa/Dropbox/dpd/inflection generator/output/sandhi/matches.csv", sep="\t", header=None)
	counts1 = df[3].value_counts()
	counts2 = df[4].value_counts()
	counts3 = df[5].value_counts()
	counts123 = pd.concat([counts1, counts2, counts3])
	output = "/home/bhikkhu/Bodhirasa/Dropbox/dpd/inflection generator/output/sandhi/count"
	counts123.to_csv(f"{output}123", sep="\t")
	counts1.to_csv(f"{output}1", header=None)
	counts2.to_csv(f"{output}2", header=None)
	counts3.to_csv(f"{output}3", header=None)
	print(f"{white}{output}1")

def sanity_test():

	print(f"{timeis()} {green}sanity test")
	print(f"{timeis()} {green}{green}{line}")

	word = random.choice(list(unmatched_set))

	if word in unmatched_set:
		print(f"{timeis()} {word} {green}in unmatched_set")
	else:
		print(f"{timeis()} {word} {green}not in unmatched_set")

	print(f"{timeis()} ")

	if word in matches2:
		print(f"{timeis()} {word} {green}in matches2")
	else:
		print(f"{timeis()} {word} {green}not in matches2")

	if word in unmatched2:
		print(f"{timeis()} {word} {green}in unmatched2")
	else:
		print(f"{timeis()} {word} {green}not in unmatched2")

	print(f"{timeis()} ")

	if word in matches3:
		print(f"{timeis()} {word} {green}in matches3")
	else:
		print(f"{timeis()} {word} {green}not in matches3")

	if word in unmatched3:
		print(f"{timeis()} {word} {green}in unmatched3")
	else:
		print(f"{timeis()} {word} {green}not in unmatched3")

	print(f"{timeis()} ")

	if word in matches4:
		print(f"{timeis()} {word} {green}in matches4")
	else:
		print(f"{timeis()} {word} {green}not in matches4")

	if word in unmatched4:
		print(f"{timeis()} {word} {green}in unmatched4")
	else:
		print(f"{timeis()} {word} {green}not in unmatched4")

	print(f"{timeis()} ")

	if word in matchesxfront:
		print(f"{timeis()} {word} {green}in matchesxfront")
	else:
		print(f"{timeis()} {word} {green}not in matchesxfront")
	
	if word in unmatchedxfront:
		print(f"{timeis()} {word} {green}in unmatchedx")
	else:
		print(f"{timeis()} {word} {green}not in unmatchedx")

	print(f"{timeis()} ")
	
	if word in unmatched_final:
		print(f"{timeis()} {word} {green}in unmatched")
	else:
		print(f"{timeis()} {word} {green}not in unmatched")

	print(f"{timeis()} {line}")


make_text_set()
import_text_set()
generate_inflected_forms_for_sandhi()
import_all_inflections_set()
generate_all_inflections_string()
make_unmatched_set()
import_sandhi_rules()
remove_exceptions()
two_word_sandhi()
three_word_sandhi()
four_word_sandhi()
# # x_word_sandhi_old()
# # x_word_sandhi_from_back()
x_word_sandhi_from_front_and_back()
summary()
make_sandhi_dict()
make_golden_dict()
unzip_and_copy()
value_counts()
sanity_test()