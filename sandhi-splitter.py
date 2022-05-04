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
from timeis import timeis, green, yellow, line, white, red
from typing import List
from pathlib import Path
from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry

warnings.filterwarnings("ignore", category=FutureWarning)

log = open("output/sandhi/log.txt", "a")

print(f"{timeis()} {line}")
print(f"{timeis()} {yellow}sandhi splitter")
print(f"{timeis()} {line}")


def make_text_set():

	print(f"{timeis()} {green}making text set")
	
	text_list = ["s0201m.mul.xml.txt"]
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

			exceptions_list = ["abbrev", "cs", "idiom", "letter","prefix", "root", "sandhi", "suffix", "ve"]

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
			
		all_inflections_set = set(inflections_string.split())

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
		all_inflections_set = pickle.load(p)

	print(f"{white}{len(all_inflections_set)}")

def make_unmatched_set():

	print(f"{timeis()} {green}making unmatched set", end = " ")
	
	global unmatched_set
	unmatched_set = sorted(text_set - all_inflections_set)
	
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
	unmatched_set = set(unmatched_set) - exceptions_set
	
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
				f2.write(f"{word}\t{wordA} + {wordB}\ttwo-word\t-\t-\t-\n")
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
						f2.write(f"{word}\t{word1} + {word2}\ttwo-word\t{rule+2}\t-\t-\n")
						
		counter += 1

	print(f"{timeis()} {green}two word matches {white}{len(matches2)} {green}(including duplicates)")

	f1.close()
	f2.close()

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
		
		if counter % 250 == 0:
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
					f2.write(f"{word}\t{wordA} + {wordB} + {wordC}\tthree-word\t-\t-\t-\n")

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
								f2.write(f"{word}\t{wordA} + {word2} + {word3}\tthree-word\t-\t{rule+2}\t-\n")
				
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
								f2.write(f"{word}\t{word1} + {word2} + {wordC}\tthree-word\t{rule+2}\t-\t-\n")

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
									f2.write(f"{word}\t{word1} + {word2} + {word3}\tthree-word\t{rulex+2}\t{ruley+2}\t-\n")
								
		counter += 1

	print(f"{timeis()} {green}three word matches {white}{len(matches3)} {green}(including duplicates)")

	f1.close()
	f2.close()

	global unmatched3
	unmatched3 = set(sorted(unmatched2)) - set(matches3)
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
						f2.write(f"{word}\t{wordA} + {wordB} + {wordC} + {wordD}\tfour-word\t-\t-\t-\n")

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
									f2.write(f"{word}\t{wordA} + {wordB} + {word3} + {word4}\tfour-word\t-\t-\t{rule+2}\n")

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
									f2.write(f"{word}\t{word1} + {word2} + {wordC} + {wordD}\tfour-word\t{rule+2}\t-\t-\n")

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
									f2.write(f"{word}\t{wordA} + {word2} + {word3} + {wordD}\tfour-word\t-\t{rule+2}\t-\n")
					
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
											f2.write(f"{word}\t{wordA} + {word2} + {word3} + {word4}\tfour-word\t-\t{rulex+2}\t{ruley+2}\n")

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
											f2.write(f"{word}\t{word1} + {word2} + {word3} + {wordD}\tfour-word\t{rulex+2}\t{ruley+2}\t-\n")

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
										f2.write(f"{word}\t{word1} + {word2} + {word3} + {word4}\tfour-word\t{rulex+2}\t-\t{ruley+2}\n")

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
												f2.write(f"{word}\t{word1} + {word2} + {word3} + {word4}\tfour-word\t{rulex+2}\t{ruley+2}\t{rulez+2}\n")

		counter += 1

	print(f"{timeis()} {green}four word matches {white}{len(matches4)} {green}(including duplicates)")

	f1.close()
	f2.close()

	global unmatched4
	unmatched4 = set(sorted(unmatched3)) - set(matches4)
	with open("output/sandhi/unmatched4.csv", "w") as f:
		for word in unmatched4:
			f.write(f"{word}\n")
			
	print(f"{timeis()} {green}four word unmatched {white}{len(unmatched4)}")


def five_word_sandhi():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}five word sandhi")
	print(f"{timeis()} {green}{line}")

	f1 = open("output/sandhi/process5.csv", "w")
	f2 = open("output/sandhi/matches.csv", "a")

	global matches5
	unmatched4 = []
	matches5 = []
	counter = 0

	unmatched4_df = pd.read_csv("output/sandhi/unmatched4.csv", header = None)
	for row in range(len(unmatched4_df)):
		word = unmatched4_df.iloc[row, 0]
		unmatched4.append(word)
	
	length = len(unmatched4)
	# print(unmatched4, length)

	for word in unmatched4:

		if counter % 100 == 0:
			print(f"{timeis()} {counter}/{length}\t{word}")

		f1.write(f"{counter}\t{word}\n")

		for w in range(0, len(word)-1):
			wordA = word[:-w-1]
			wordA_lastletter = wordA[len(wordA)-1]

			for x in range(0, len(word[-1-w:])-1):
				wordB = word[-1-w:-x-1]
				wordB_firstletter = wordB[0]
				wordB_lastletter = wordB[len(wordB)-1]
				wordC = word[-1-x:]
				wordC_firstletter = wordC[0]

				for y in range(0, len(word[-1-x:])-1):
					wordC = word[-1-x:-y-1]
					wordC_firstletter = wordC[0]
					wordC_lastletter = wordC[len(wordC)-1]
					wordD = word[-1-y:]
					wordD_firstletter = wordD[0]

					for z in range(0, len(word[-1-y:])-1):
						wordD = word[-1-y:-z-1]
						wordD_firstletter = wordD[0]
						wordD_lastletter = wordD[len(wordD)-1]
						wordE = word[-1-z:]
						wordE_firstletter = wordE[0]

						# f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\t{wordE}\n") # too big!!!

					# # blah blah blah blah blah

					# if \
					# wordA in all_inflections_set and \
					# wordB in all_inflections_set and \
					# wordC in all_inflections_set and \
					# wordD in all_inflections_set and \
					# wordE in all_inflections_set:
					# 	matches5.append(word)
					# 	# f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\t{wordE}\t-\t-\t-\t-\tmatch\n")
					# 	f2.write(f"{word}\t{wordA} + {wordB} + {wordC} + {wordD} + {wordE}\tfive-word\t-\t-\t-\n")

					# bla* *la* *la* *la* *lah

						for rulew in rules:
							chAw = rules[rulew].get("chA")
							chBw = rules[rulew].get("chB")
							ch1w = rules[rulew].get("ch1")
							ch2w = rules[rulew].get("ch2")

							if \
							wordA_lastletter == chAw and \
							wordB_firstletter == chBw:
								word1 = wordA[:-1] + ch1w
								word2 = ch2w + wordB[1:]
								f1.write(
									f"\t{word1}\t{word2}\t{wordC}\t{wordD}\t{wordE}\t{rulew+2}\t-\t-\t-\n")

								for rulex in rules:
									chAx = rules[rulex].get("chA")
									chBx = rules[rulex].get("chB")
									ch1x = rules[rulex].get("ch1")
									ch2x = rules[rulex].get("ch2")

									if \
									wordB_lastletter == chAx and \
									wordC_firstletter == chBx:
										word2 = (ch2w + wordB[1:])[:-1] + ch1x
										word3 = ch2x + wordC[1:]
										f1.write(f"\t{word1}\t{word2}\t{word3}\t{wordD}\t{wordE}\t{rulew+2}\t{rulex+2}\t-\t-\n")

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
												f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{wordE}\t{rulew+2}\t{rulex+2}\t{ruley+2}\t-\n")


												for rulez in rules:
													chAz = rules[ruley].get("chA")
													chBz = rules[ruley].get("chB")
													ch1z = rules[ruley].get("ch1")
													ch2z = rules[ruley].get("ch2")

													if \
													wordD_lastletter == chAz and \
													wordE_firstletter == chBz:
														word4 = (ch2y + wordD[1:])[:-1] + ch1z
														word5 = ch2z + wordD[1:]

														if \
														word1 in all_inflections_set and \
														word2 in all_inflections_set and \
														word3 in all_inflections_set and \
														word4 in all_inflections_set and \
														word5 in all_inflections_set:
															matches5.append(word)
															f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{word5}\t{rulew+2}\t{rulex+2}\t{ruley+2}\t{rulez+2}\tmatch\n")
															f2.write(
																f"{word}\t{word1} + {word2} + {word3} + {word4} + {word5}\tfive-word\t{rulew+2}\t{rulex+2}\t{ruley+2}\t{rulez+2}\n")

	# 				# blah blah bla* *lah

	# 				if \
    #                                             wordA in all_inflections_set and \
    #                                             wordB in all_inflections_set:

	# 					for rule in rules:
	# 						chA = rules[rule].get("chA")
	# 						chB = rules[rule].get("chB")
	# 						ch1 = rules[rule].get("ch1")
	# 						ch2 = rules[rule].get("ch2")

	# 						if \
    #                                                             wordC_lastletter == chA and \
    #                                                             wordD_firstletter == chB:
	# 							word3 = wordC[:-1] + ch1
	# 							word4 = ch2 + wordD[1:]

	# 							if \
    #                                                                     word3 in all_inflections_set and \
    #                                                                     word4 in all_inflections_set:
	# 								matches4.append(word)
	# 								f1.write(
	# 									f"\t{wordA}\t{wordB}\t{word3}\t{word4}\t-\t-\t{rule+2}\tmatch\n")
	# 								f2.write(
	# 									f"{word}\t{wordA} + {wordB} + {word3} + {word4}\tfour-word\t-\t-\t{rule+2}\n")

	# 				# bla* *lah blah blah

	# 				if \
    #                                             wordC in all_inflections_set and \
    #                                             wordD in all_inflections_set:

	# 					for rule in rules:
	# 						chA = rules[rule].get("chA")
	# 						chB = rules[rule].get("chB")
	# 						ch1 = rules[rule].get("ch1")
	# 						ch2 = rules[rule].get("ch2")

	# 						if \
    #                                                             wordA_lastletter == chA and \
    #                                                             wordB_firstletter == chB:
	# 							word1 = wordA[:-1] + ch1
	# 							word2 = ch2 + wordB[1:]

	# 							if \
    #                                                                     word1 in all_inflections_set and \
    #                                                                     word2 in all_inflections_set:
	# 								matches4.append(word)
	# 								f1.write(
	# 									f"\t{word1}\t{word2}\t{wordC}\t{wordD}\t{rule+2}-\t-\t\tmatch\n")
	# 								f2.write(
	# 									f"{word}\t{word1} + {word2} + {wordC} + {wordD}\tfour-word\t{rule+2}\t-\t-\n")

	# 				# blah bla* *lah blah

	# 				if \
    #                                             wordA in all_inflections_set and \
    #                                             wordD in all_inflections_set:

	# 					for rule in rules:
	# 						chA = rules[rule].get("chA")
	# 						chB = rules[rule].get("chB")
	# 						ch1 = rules[rule].get("ch1")
	# 						ch2 = rules[rule].get("ch2")

	# 						if \
    #                                                             wordB_lastletter == chA and \
    #                                                             wordC_firstletter == chB:
	# 							word2 = wordB[:-1] + ch1
	# 							word3 = ch2 + wordC[1:]

	# 							if \
    #                                                                     word2 in all_inflections_set and \
    #                                                                     word3 in all_inflections_set:
	# 								matches4.append(word)
	# 								f1.write(
	# 									f"\t{wordA}\t{word2}\t{word3}\t{wordD}\t-\t{rule+2}\t-\tmatch\n")
	# 								f2.write(
	# 									f"{word}\t{wordA} + {word2} + {word3} + {wordD}\tfour-word\t-\t{rule+2}\t-\n")

	# 				# blah bla* *la* *lah

	# 				if wordA in all_inflections_set:

	# 					for rulex in rules:
	# 						chAx = rules[rulex].get("chA")
	# 						chBx = rules[rulex].get("chB")
	# 						ch1x = rules[rulex].get("ch1")
	# 						ch2x = rules[rulex].get("ch2")

	# 						if \
    #                                                             wordB_lastletter == chAx and \
    #                                                             wordC_firstletter == chBx:
	# 							word2 = wordB[:-1] + ch1x
	# 							word3 = ch2x + wordC[1:]

	# 							for ruley in rules:
	# 								chAy = rules[ruley].get("chA")
	# 								chBy = rules[ruley].get("chB")
	# 								ch1y = rules[ruley].get("ch1")
	# 								ch2y = rules[ruley].get("ch2")

	# 								if \
    #                                                                             wordC_lastletter == chAy and \
    #                                                                             wordD_firstletter == chBy:
	# 									word3 = (ch2x + wordB[1:])[:-1] + ch1y
	# 									word4 = ch2y + wordC[1:]

	# 									if \
    #                                                                                     word2 in all_inflections_set and \
    #                                                                                     word3 in all_inflections_set and \
    #                                                                                     word4 in all_inflections_set:
	# 										matches4.append(word)
	# 										f1.write(
	# 											f"\t{wordA}\t{word2}\t{word3}\t{word4}\t-\t{rulex+2}\t{ruley+2}\tmatch\n")
	# 										f2.write(
	# 											f"{word}\t{wordA} + {word2} + {word3} + {word4}\tfour-word\t-\t{rulex+2}\t{ruley+2}\n")

	# 				# bla* *la* *lah blah

	# 				if wordD in all_inflections_set:

	# 					for rulex in rules:
	# 						chAx = rules[rulex].get("chA")
	# 						chBx = rules[rulex].get("chB")
	# 						ch1x = rules[rulex].get("ch1")
	# 						ch2x = rules[rulex].get("ch2")

	# 						if \
    #                                                             wordA_lastletter == chAx and \
    #                                                             wordB_firstletter == chBx:
	# 							word1 = wordA[:-1] + ch1x
	# 							word2 = ch2x + wordB[1:]

	# 							for ruley in rules:
	# 								chAy = rules[ruley].get("chA")
	# 								chBy = rules[ruley].get("chB")
	# 								ch1y = rules[ruley].get("ch1")
	# 								ch2y = rules[ruley].get("ch2")

	# 								if \
    #                                                                             wordB_lastletter == chAy and \
    #                                                                             wordC_firstletter == chBy:
	# 									word2 = (ch2x + wordB[1:])[:-1] + ch1y
	# 									word3 = ch2y + wordC[1:]

	# 									if \
    #                                                                                     word1 in all_inflections_set and \
    #                                                                                     word2 in all_inflections_set and \
    #                                                                                     word3 in all_inflections_set:
	# 										matches4.append(word)
	# 										f1.write(
	# 											f"\t{word1}\t{word2}\t{word3}\t{wordD}\t{rulex+2}\t{ruley+2}\t-\tmatch\n")
	# 										f2.write(
	# 											f"{word}\t{word1} + {word2} + {word3} + {wordD}\tfour-word\t{rulex+2}\t{ruley+2}\t-\n")

	# 				# bla* *lah bla* *lah

	# 				for rulex in rules:
	# 					chAx = rules[rulex].get("chA")
	# 					chBx = rules[rulex].get("chB")
	# 					ch1x = rules[rulex].get("ch1")
	# 					ch2x = rules[rulex].get("ch2")

	# 					if \
    #                                                     wordA_lastletter == chAx and \
    #                                                     wordB_firstletter == chBx:
	# 						word1 = wordA[:-1] + ch1x
	# 						word2 = ch2x + wordB[1:]

	# 						for ruley in rules:
	# 							chAy = rules[ruley].get("chA")
	# 							chBy = rules[ruley].get("chB")
	# 							ch1y = rules[ruley].get("ch1")
	# 							ch2y = rules[ruley].get("ch2")

	# 							if \
    #                                                                     wordC_lastletter == chAy and \
    #                                                                     wordD_firstletter == chBy:
	# 								word3 = wordC[:-1] + ch1y
	# 								word4 = ch2y + wordD[1:]

	# 								if \
    #                                                                             word1 in all_inflections_set and \
    #                                                                             word2 in all_inflections_set and \
    #                                                                             word3 in all_inflections_set and \
    #                                                                             word4 in all_inflections_set:
	# 									matches4.append(word)
	# 									f1.write(
	# 										f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t-\t{ruley+2}\tmatch\n")
	# 									f2.write(
	# 										f"{word}\t{word1} + {word2} + {word3} + {word4}\tfour-word\t{rulex+2}\t-\t{ruley+2}\n")



		counter += 1

	# print(f"{timeis()} {green}four word matches {white}{len(matches4)} {green}(including duplicates)")

	# f1.close()
	# f2.close()

	# global unmatched4
	# unmatched4 = set(sorted(unmatched3)) - set(matches4)
	# with open("output/sandhi/unmatched4.csv", "w") as f:
	# 	for word in unmatched4:
	# 		f.write(f"{word}\n")

	# print(f"{timeis()} {green}four word unmatched {white}{len(unmatched4)}")

def summary():

	print(f"{timeis()} {green}{line}")
	print(f"{timeis()} {green}summary")
	print(f"{timeis()} {green}{line}")

	global unmatched_final
	unmatched_final=set(unmatched_set) - set(matches2) - set(matches3) - set(matches4)

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

	zip_path = Path("./output/sandhi/DPD SSS MN1mūla.zip")

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
		{"bookname": "DPD Sandhi Splitter",
			"author": "Bodhirasa",
			"description": "",
			"website": "",}
			)

	export_words_as_stardict_zip(words, ifo, zip_path)	

	print(f"{white}ok")

def unzip_and_copy():

	print(f"{timeis()} {green}unipping and copying goldendict", end = " ")

	os.popen('unzip -o "output/sandhi/DPD Sandhi Splitter.zip" -d "/home/bhikkhu/Documents/Golden Dict"')
	
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
	
	if word in unmatched_final:
		print(f"{timeis()} {word} {green}in unmatched")
	else:
		print(f"{timeis()} {word} {green}not in unmatched")

	print(f"{timeis()} {line}")


make_text_set()
import_text_set()
generate_inflected_forms_for_sandhi()
import_all_inflections_set()
make_unmatched_set()
import_sandhi_rules()
remove_exceptions()
two_word_sandhi()
three_word_sandhi()
four_word_sandhi()
# five_word_sandhi()
summary()
make_sandhi_dict()
make_golden_dict()
unzip_and_copy()
value_counts()
sanity_test()