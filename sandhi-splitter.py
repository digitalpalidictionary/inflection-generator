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
from difflib import SequenceMatcher
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
	text_set = set(text_string.split())

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
	unmatched_set = text_set - set(all_inflections_set)
	
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
	f2.write(f"word\tsplit\tprocess\trules\n")

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

			if wordA in all_inflections_set:
				if wordB in all_inflections_set:
					f1.write(f"\t{wordA}\t{wordB}\t-\t-\tmatch\n")
					f2.write(f"{word}\t{wordA}-{wordB}\ttwo-word\t0\n")
					matches2.append(word)
			
			# bla* *lah
			
			for rule in rules:
				chA = rules[rule].get("chA")
				chB = rules[rule].get("chB")	
				ch1 = rules[rule].get("ch1")
				ch2 = rules[rule].get("ch2")
				
				if wordA_lastletter == chA:
					if wordB_firstletter == chB:
						word1 = wordA[:-1] + ch1
						word2 = ch2 + wordB[1:]

						if word1 in all_inflections_set:
							if word2 in all_inflections_set:
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

						if wordB_lastletter == chA:
							if wordC_firstletter == chB:
								word2 = wordB[:-1] + ch1
								word3 = ch2 + wordC[1:]

								if wordA in all_inflections_set:
									if word2 in all_inflections_set:
										if word3 in all_inflections_set:
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

						if wordA_lastletter == chA:
							if wordB_firstletter == chB:
								word1 = wordA[:-1] + ch1
								word2 = ch2 + wordB[1:]

								if word1 in all_inflections_set:
									if word2 in all_inflections_set:
										if wordC in all_inflections_set:
											matches3.append(word)
											f1.write(f"\t{word1}\t{word2}\t{wordC}\t{rule+2}\t-\tmatch\n")
											f2.write(f"{word}\t{word1}-{word2}-{wordC}\tthree-word\t{rule+2},0\n")

				# bla* *la* *lah
				
				for rulex in rules:
					chAx = rules[rulex].get("chA")
					chBx = rules[rulex].get("chB")
					ch1x = rules[rulex].get("ch1")
					ch2x = rules[rulex].get("ch2")

					if wordA_lastletter == chAx:
						if wordB_firstletter == chBx:
							word1 = wordA[:-1] + ch1x
							word2 = ch2x + wordB[1:]
						
							for ruley in rules:
								chAy = rules[ruley].get("chA")
								chBy = rules[ruley].get("chB")
								ch1y = rules[ruley].get("ch1")
								ch2y = rules[ruley].get("ch2")

								if wordB_lastletter == chAy:
									if wordC_firstletter == chBy:
										word2 = (ch2x + wordB[1:])[:-1] + ch1y
										word3 = ch2y + wordC[1:]

										if word1 in all_inflections_set:
											if word2 in all_inflections_set:
												if word3 in all_inflections_set:
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

					if wordA in all_inflections_set:
						if wordB in all_inflections_set:
							if wordC in all_inflections_set:
								if wordD in all_inflections_set:
									matches4.append(word)
									f1.write(f"\t{wordA}\t{wordB}\t{wordC}\t{wordD}\t-\t-\t-\tmatch\n")
									f2.write(f"{word}\t{wordA}-{wordB}-{wordC}-{wordD}\tfour-word\t0,0,0\n")

					# blah blah bla* *lah

					if wordA in all_inflections_set:
						if wordB in all_inflections_set:
							
							for rule in rules:
								chA = rules[rule].get("chA")
								chB = rules[rule].get("chB")
								ch1 = rules[rule].get("ch1")
								ch2 = rules[rule].get("ch2")

								if wordC_lastletter == chA:
									if wordD_firstletter == chB:
										word3 = wordC[:-1] + ch1
										word4 = ch2 + wordD[1:]

										if word3 in all_inflections_set:
											if word4 in all_inflections_set:
												matches4.append(word)
												f1.write(f"\t{wordA}\t{wordB}\t{word3}\t{word4}\t-\t-\t{rule+2}\tmatch\n")
												f2.write(f"{word}\t{wordA}-{wordB}-{word3}-{word4}\tfour-word\t0,0,{rule+2}\n")

					# bla* *lah blah blah

					if wordC in all_inflections_set:
						if wordD in all_inflections_set:

							for rule in rules:
								chA = rules[rule].get("chA")
								chB = rules[rule].get("chB")
								ch1 = rules[rule].get("ch1")
								ch2 = rules[rule].get("ch2")

								if wordA_lastletter == chA:
									if wordB_firstletter == chB:
										word1 = wordA[:-1] + ch1
										word2 = ch2 + wordB[1:]

										if word1 in all_inflections_set:
											if word2 in all_inflections_set:
												matches4.append(word)
												f1.write(f"\t{word1}\t{word2}\t{wordC}\t{wordD}\t{rule+2}-\t-\t\tmatch\n")
												f2.write(f"{word}\t{word1}-{word2}-{wordC}-{wordD}\tfour-word\t{rule+2},0,0\n")

					# blah bla* *lah blah

					if wordA in all_inflections_set:
						if wordD in all_inflections_set:

							for rule in rules:
								chA = rules[rule].get("chA")
								chB = rules[rule].get("chB")
								ch1 = rules[rule].get("ch1")
								ch2 = rules[rule].get("ch2")

								if wordB_lastletter == chA:
									if wordC_firstletter == chB:
										word2 = wordB[:-1] + ch1
										word3 = ch2 + wordC[1:]

										if word2 in all_inflections_set:
											if word3 in all_inflections_set:
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

							if wordB_lastletter == chAx:
								if wordC_firstletter == chBx:
									word2 = wordB[:-1] + ch1x
									word3 = ch2x + wordC[1:]

									for ruley in rules:
										chAy = rules[ruley].get("chA")
										chBy = rules[ruley].get("chB")
										ch1y = rules[ruley].get("ch1")
										ch2y = rules[ruley].get("ch2")

										if wordC_lastletter == chAy:
											if wordD_firstletter == chBy:
												word3 = (ch2x + wordC[1:])[:-1] + ch1y
												word4 = ch2y + wordD[1:]

												if word2 in all_inflections_set:
													if word3 in all_inflections_set:
														if word4 in all_inflections_set:
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

							if wordA_lastletter == chAx:
								if wordB_firstletter == chBx:
									word1 = wordA[:-1] + ch1x
									word2 = ch2x + wordB[1:]

									for ruley in rules:
										chAy = rules[ruley].get("chA")
										chBy = rules[ruley].get("chB")
										ch1y = rules[ruley].get("ch1")
										ch2y = rules[ruley].get("ch2")

										if wordB_lastletter == chAy:
											if wordC_firstletter == chBy:
												word2 = (ch2x + wordB[1:])[:-1] + ch1y
												word3 = ch2y + wordC[1:]

												if word1 in all_inflections_set:
													if word2 in all_inflections_set:
														if word3 in all_inflections_set:
															matches4.append(word)
															f1.write(f"\t{word1}\t{word2}\t{word3}\t{wordD}\t{rulex+2}\t{ruley+2}\t-\tmatch\n")
															f2.write(f"{word}\t{word1}-{word2}-{word3}-{wordD}\tfour-word\t{rulex+2},{ruley+2},0\n")

					# bla* *lah bla* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if wordA_lastletter == chAx:
							if wordB_firstletter == chBx:
								word1 = wordA[:-1] + ch1x
								word2 = ch2x + wordB[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if wordC_lastletter == chAy:
										if wordD_firstletter == chBy:
											word3 = wordC[:-1] + ch1y
											word4 = ch2y + wordD[1:]

											if word1 in all_inflections_set:
												if word2 in all_inflections_set:
													if word3 in all_inflections_set:
														if word4 in all_inflections_set:
															matches4.append(word)
															f1.write(f"\t{word1}\t{word2}\t{word3}\t{word4}\t{rulex+2}\t-\t{ruley+2}\tmatch\n")
															f2.write(f"{word}\t{word1}-{word2}-{word3}-{word4}\tfour-word\t{rulex+2},0,{ruley+2}\n")

					# bla* *la* *la* *lah

					for rulex in rules:
						chAx = rules[rulex].get("chA")
						chBx = rules[rulex].get("chB")
						ch1x = rules[rulex].get("ch1")
						ch2x = rules[rulex].get("ch2")

						if wordA_lastletter == chAx:
							if wordB_firstletter == chBx:
								word1 = wordA[:-1] + ch1x
								word2 = ch2x + wordB[1:]

								for ruley in rules:
									chAy = rules[ruley].get("chA")
									chBy = rules[ruley].get("chB")
									ch1y = rules[ruley].get("ch1")
									ch2y = rules[ruley].get("ch2")

									if wordB_lastletter == chAy:
										if wordC_firstletter == chBy:
											word2 = (ch2x + wordB[1:])[:-1] + ch1y
											word3 = ch2y + wordC[1:]

											for rulez in rules:
												chAz = rules[rulez].get("chA")
												chBz = rules[rulez].get("chB")
												ch1z = rules[rulez].get("ch1")
												ch2z = rules[rulez].get("ch2")

												if wordC_lastletter == chAz:
													if wordD_firstletter == chBz:
														word3 =(ch2y + wordC[1:])[:-1] + ch1z
														word4 = ch2z + wordD[1:]

														if word1 in all_inflections_set:
															if word2 in all_inflections_set:
																if word3 in all_inflections_set:
																	if word4 in all_inflections_set:
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

					if wordA_lastletter == chA:
						if wordB_firstletter == chB:
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

				# # find negatives

				# if len(tried) == 1:

				# 	neg_list = ["a", "an", "na"]

				# 	for neg in neg_list:
					
				# 		if re.findall(f"^{neg}", word):
				# 			f1.write(f"\n\tneg in front:\t{neg}\n")
				# 			if printme:
				# 				print(f"{timeis()} neg in front: {neg}")

				# 			word1 = neg
				# 			word2 = word[len(neg):]
				# 			f1.write(f"\tneg wordAB:\t{word1}\t{word2}\n")
				# 			if printme:
				# 				print(f"{timeis()} neg wordAB:\t{word1}-{word2}")
							
				# 			test = re.findall(f",{word2[:3]}", all_inflections_string)
				# 			f1.write(f"\ttest word2: \t{test[:5]}\n")
				# 			if printme:
				# 				print(f"{timeis()} test word2: \t{test[:5]}")

				# 			if test != []:
				# 				word_front_to_recurse = f"{word1}-"
				# 				word_to_recurse = word2
				# 				f1.write(f"\tneg fin:\t{word_front_to_recurse}\t{word_to_recurse}\t{word_back}\n")
				# 				if printme:
				# 					print(f"{timeis()} neg fin: {green}{word_front_to_recurse}{blue}{word_to_recurse}{yellow}{word_back}\n")
				# 				comment = f"neg {neg}"
				# 				rules_front_to_recruse = rules_front + [-1]
				# 				split_from_front_and_back(word_initial, word_front_to_recurse, word_to_recurse, word_back, comment, rules_front_to_recruse, rules_back)

				# find longest fuzzy words from the front
				
				def find_longest_word_fuzzy(word):

					lwff_fuzzy_list = []
					lwfb_fuzzy_list = []
					f1.write(f"\n")

					for x in range(len(word)-1): # one letter front, one back
						wordA = word[:1+x]
						wordB = word[1+x:]

						fuzzy_searchA = re.findall(f",{wordA[:-1]}.,", all_inflections_string)
						f1.write(f"\tfuzzysearchA\t{fuzzy_searchA}\n")
						if printme:
							print(f"{timeis()} fuzzysearchA\t{fuzzy_searchA}")

						if fuzzy_searchA != []:
							if len(wordA) > 0:
								if lwff_fuzzy_list == []:
									lwff_fuzzy_list = [wordA]
								else:
									lwff_fuzzy_list = [wordA] + lwff_fuzzy_list

						fuzzy_searchB = re.findall(f",.{wordB[1:]},", all_inflections_string)
						if printme:
							print(f"{timeis()} fuzzysearchB\t{fuzzy_searchB}")

						if fuzzy_searchB != []:
							if len(wordB) > 0:
								if lwfb_fuzzy_list  == []:
									lwfb_fuzzy_list = [wordB]
								else:
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

				# prune the lists - use first 3
				
				if len(lwff_fuzzy_list) > 1:
					lwff_fuzzy_list = lwff_fuzzy_list[0:1]

				if len(lwfb_fuzzy_list) > 1:
					lwfb_fuzzy_list = lwfb_fuzzy_list[0:1]


				# split fuzzy front, run rules and recurse

				for lwff_fuzzy in lwff_fuzzy_list:
					if len(lwff_fuzzy) > 2:
					
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
							
							if wordA_lastletter == chA:
								if wordB_firstletter == chB:
									word1 = wordA_fuzzy[:-1] + ch1
									word2 = ch2 + wordB_fuzzy[1:]

									f1.write(f"\tfuzzy words front:\t{word1}-{word2}\n")
									if printme:  
										print(f"{timeis()} fuzzy words front: {green}{word1}-{blue}{word2}")

									if word1 in all_inflections_set:
										test = re.findall(f",{word2[:3]}", all_inflections_string)
										f1.write(f"\ttestword2\t{test[:5]}\n")
										if printme:  
											print(f"{timeis()} testword2\t{test[:5]}")

										if test != []:
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
					if len(lwfb_fuzzy) > 3:

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

							if wordA_lastletter == chA:
								if wordB_firstletter == chB:
									word1 = wordA_fuzzy[:-1] + ch1
									word2 = ch2 + wordB_fuzzy[1:]

									f1.write(f"\tfuzzy words back:\t{word1}-{word2}\n")
									if printme:
										print(f"{timeis()} fuzzy words back: {green}{word1}-{blue}{word2}")

									if word2 in all_inflections_set:
										test = re.findall(f"{word1[-3:]}.,", all_inflections_string)
										f1.write(f"\ttestword1\t{test[:5]}\n")
										if printme:
											print(f"{timeis()} testword1\t{test[:5]}")

										if test != []:
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

						if clean_searchA != False:
							if len(wordA) > 0:
								if lwff_clean_list == []:
									lwff_clean_list = [wordA]
								else:
									lwff_clean_list = [wordA] + lwff_clean_list
						
						clean_searchB = wordB in all_inflections_set

						if clean_searchB != False:
							if len(wordB) > 0:
								if lwfb_clean_list == []:
									lwfb_clean_list = [wordB]
								else:
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

				# prune lists - use first 3

				if len(lwff_clean_list) > 1:
					lwff_clean_list = lwff_clean_list[0:1]

				if len(lwfb_clean_list) > 1:
					lwfb_clean_list = lwfb_clean_list[0:1]

				# split clean front, run rules and recurse

				for lwff_clean in lwff_clean_list:
					
					if len(lwff_clean) > 2:

						wordA = lwff_clean
						wordB = re.sub(f"^{wordA}", "", word)
						f1.write(f"\n\tclean words front:\t{wordA}\t{wordB}\n")
						if printme:
							print(f"{timeis()} clean words front: {green}{wordA}-{blue}{wordB}")

						test = re.findall(f",{wordB[:3]}", all_inflections_string)
						f1.write(f"\ttestB\t{sorted(set(test))}\n")
						if printme:
							print(f"{timeis()} testB\t{sorted(set(test))}")

						if test != []:

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

					if len(lwfb_clean) > 3:

						wordB = lwfb_clean
						wordA = re.sub(f"{wordB}$", "", word)
						f1.write(f"\n\tclean words back:\t{wordA}\t{wordB}\n")
						if printme:
							print(f"{timeis()} clean words back: {green}{wordA}-{blue}{wordB}")

						test = re.findall(f"{wordA[-3:]},", all_inflections_string)
						f1.write(f"\ttestA\t{sorted(set(test))}\n")
						if printme:
							print(f"{timeis()} testA\t{sorted(set(test))}")

						if test != []:

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
		
		if counter % 100 == 0:
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

def make_sandhi_dict():

	print(f"{timeis()} {green}saving matches_df", end=" ")

	matches_df = pd.read_csv("output/sandhi/matches.csv", dtype=str, sep="\t")
	matches_df = matches_df.fillna("")
	# matches_df.drop(['process', 'rules'], inplace=True, axis=1)
	
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
	
	sandhi_dict = {}

	for row in range(len(matches_df)):
		word = matches_df.loc[row, 'word']
		split = matches_df.loc[row, 'split']
		ratio = matches_df.loc[row, 'ratio']
		rulez = matches_df.loc[row, 'rules']

		if word not in sandhi_dict.keys():
			sandhi_dict.update({word: [f"{split} ({rulez}) ({ratio:.4f})"]})

		if word in sandhi_dict.keys() and \
			len(sandhi_dict[word]) < 5 and \
				f"{split} ({rulez}) ({ratio:.4f})" not in sandhi_dict[word]:
			sandhi_dict[word].append(f"{split} ({rulez}) ({ratio:.4f})")

	matches_df = pd.DataFrame(sandhi_dict.items())
	matches_df.rename({0: "word", 1: "split"}, axis='columns', inplace=True)
	matches_df.to_csv("output/sandhi/matches_df.csv", index=None, sep="\t")
	
	print(f"{white}ok")

def make_golden_dict():

	print(f"{timeis()} {green}generating goldendict", end=" ")
	
	df = pd.read_csv("output/sandhi/matches_df.csv", sep="\t", dtype=str)
	df = df.fillna("")

	df["split"] = df["split"].str.replace(r"\[|\]", "")
	df["split"] = df["split"].str.replace("'", "")
	df["split"] = df["split"].str.replace('"', "")
	df["split"] = df["split"].str.replace(r"\), ", ")<br>")
	df["split"] = df["split"].str.replace(", ", ",")

	df.insert(2, "definition_plain", "")
	df.insert(3, "synonyms", "")
	df.rename({"word": "word", "split": "definition_html"}, axis='columns', inplace=True)
	
	df.to_json("output/sandhi/matches.json", force_ascii=False, orient="records", indent=5)

	zip_path = Path("./output/sandhi/padavibhāga MN2.zip")
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
		{"bookname": "padavibhāga MN2",
			"author": "Bodhirasa",
			"description": "",
			"website": "",}
			)

	export_words_as_stardict_zip(words, ifo, zip_path)	

	print(f"{white}ok")

def unzip_and_copy():

	print(f"{timeis()} {green}unipping and copying goldendict", end = " ")

	os.popen('unzip -o "output/sandhi/padavibhāga MN2" -d "/home/bhikkhu/Documents/Golden Dict"')
	
	print(f"{white}ok")
	print(f"{timeis()} {green}{line}")

def value_counts():

	print(f"{timeis()} {green}saving value counts", end=" ")
	matches_df = pd.read_csv("output/sandhi/matches.csv", sep="\t")
	
	rules_string = ""

	for row in range(len(matches_df)):
		rulez = matches_df.loc[row, 'rules']
		rulez = re.sub("'", "", rulez)
		rulez = re.sub("\[|\]", "", rulez)
		rules_string = rules_string + rulez + ","

	rules_df = pd.DataFrame(rules_string.split(","))
	# print(rules_df)
	
	counts = rules_df.value_counts()
	counts.to_csv(f"output/sandhi/counts", sep="\t")

	print(f"{white}ok")

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

	if word in matchesx:
		print(f"{timeis()} {word} {green}in matchesx")
	else:
		print(f"{timeis()} {word} {green}not in matchesx")
	
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
x_word_sandhi_from_front_and_back()
summary()
make_sandhi_dict()
make_golden_dict()
unzip_and_copy()
value_counts()
sanity_test()