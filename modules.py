#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import re
import pickle
import os
from aksharamukha import transliterate
from datetime import datetime
import json
from timeis import timeis, blue, yellow, green, red, white, line, tic, toc
from io import StringIO
from csv import writer
from sorter import sort_key


def create_inflection_table_index():

	print(f"{timeis()} {yellow}inflection generator")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}creating inflection table index")

	global inflection_table_index_df
	inflection_table_index_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="index", dtype=str)

	inflection_table_index_df.fillna("", inplace=True)

	global inflection_table_index_length
	inflection_table_index_length = len(inflection_table_index_df)

	global inflection_table_index_dict
	inflection_table_index_dict = dict(zip(inflection_table_index_df.iloc[:, 0], inflection_table_index_df.iloc[:, 2]))


def generate_inflection_tables_dict():
	print(f"{timeis()} {green}creating dict of inflection table dataframes")

	inflection_tables_dict = {}

	inflection_table_df = pd.read_excel(
		"declensions & conjugations.xlsx", sheet_name="declensions", dtype=str)

	inflection_table_df = inflection_table_df.shift(periods=2)

	inflection_table_df.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", 
	"K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", 
	"AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", 
	"AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ", 
	"BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK", "BL", "BM", 
	"BN", "BO", "BP", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BX", "BY", "BZ", 
	"CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM", 
	"CN", "CO", "CP", "CQ", "CR", "CS", "CT", "CU", "CV", "CW", "CX", "CY", "CZ", 
	"DA", "DB", "DC", "DD", "DE", "DF", "DG", "DH", "DI", "DJ", "DK"]

	inflection_table_df.fillna("", inplace=True)

	for row in range(inflection_table_index_length):
		inflection_name = inflection_table_index_df.iloc[row, 0]
		cell_range = inflection_table_index_df.iloc[row, 1]
		like = inflection_table_index_df.iloc[row, 2]

		col_range_1 = re.sub("(.+?)\d*\:.+", "\\1", cell_range)
		col_range_2 = re.sub(".+\:(.[A-Z]*)\d*", "\\1", cell_range)
		row_range_1 = int(re.sub(".+?(\d{1,3}):.+", "\\1", cell_range))
		row_range_2 = int(re.sub(".+:.+?(\d{1,3})", "\\1", cell_range))

		inflection_table_df_filtered = inflection_table_df.loc[row_range_1:row_range_2, col_range_1:col_range_2]
		inflection_table_df_filtered.name = f"{inflection_name}"
		inflection_table_df_filtered.reset_index(drop=True, inplace=True)
		inflection_table_df_filtered.iloc[0, 0] = "" # remove inflection name
		
		# replace header
		new_header = inflection_table_df_filtered.iloc[0] #grab the first row for the header
		inflection_table_df_filtered = inflection_table_df_filtered[1:] #take the data less the header row
		inflection_table_df_filtered.columns = new_header #set the header row as the df header

		# replace index
		inflection_table_df_filtered.index = inflection_table_df_filtered.iloc[0:, 0]
		inflection_table_df_filtered = inflection_table_df_filtered.iloc[:, 1:]
		inflection_table_df_filtered.rename_axis(None, axis=1, inplace=True)  # delete pattern name

		inflection_tables_dict[inflection_name] = {}
		inflection_tables_dict[inflection_name]["df"] = inflection_table_df_filtered
		inflection_tables_dict[inflection_name]["range"] = cell_range
		inflection_tables_dict[inflection_name]["like"] = like
	
	with open("output/inflection tables dict", "wb") as f:
		pickle.dump(inflection_tables_dict, f)


def create_inflection_table_df():
	print(f"{timeis()} {green}creating inflection table dataframe")

	global inflection_table_df
	inflection_table_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="declensions", dtype=str)

	inflection_table_df = inflection_table_df.shift(periods=2)

	inflection_table_df.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK", "BL", "BM", "BN", "BO", "BP", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BX", "BY", "BZ", "CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM", "CN", "CO", "CP", "CQ", "CR", "CS", "CT", "CU", "CV", "CW", "CX", "CY", "CZ", "DA", "DB", "DC", "DD", "DE", "DF", "DG", "DH", "DI", "DJ", "DK"]

	inflection_table_df.fillna("", inplace=True)
	# print(inflection_table_df[:20])


def test_inflection_pattern_changed():
	print(f"{timeis()} {green}test if inflection table has changed")
	
	global inflection_tables_dict
	with open("output/inflection tables dict", "rb") as f:
		inflection_tables_dict = pickle.load(f)

	global pattern_changed
	pattern_changed = []

	for row in range(inflection_table_index_length):
		inflection_name = inflection_table_index_df.iloc[row,0]
		cell_range = inflection_table_index_df.iloc[row,1]
		like = inflection_table_index_df.iloc[row,2]

		col_range_1 = re.sub("(.+?)\d*\:.+", "\\1", cell_range)
		col_range_2 = re.sub(".+\:(.[A-Z]*)\d*", "\\1", cell_range)
		row_range_1 = int(re.sub(".+?(\d{1,3}):.+", "\\1", cell_range))
		row_range_2 = int(re.sub(".+:.+?(\d{1,3})", "\\1", cell_range))

		inflection_table_df_filtered = inflection_table_df.loc[row_range_1:row_range_2, col_range_1:col_range_2]
		inflection_table_df_filtered.name =  f"{inflection_name}"
		inflection_table_df_filtered.reset_index(drop=True, inplace=True)
		inflection_table_df_filtered.iloc[0,0] = ""

		# replace header
		new_header = inflection_table_df_filtered.iloc[0] #grab the first row for the header
		inflection_table_df_filtered = inflection_table_df_filtered[1:] #take the data less the header row
		inflection_table_df_filtered.columns = new_header #set the header row as the df header

		# replace index
		inflection_table_df_filtered.index = inflection_table_df_filtered.iloc[0:,0]
		inflection_table_df_filtered = inflection_table_df_filtered.iloc[:, 1:]
		inflection_table_df_filtered.rename_axis(None, axis=1, inplace=True)  # delete pattern name

		# test
		try:
			old_table = inflection_tables_dict[inflection_name]["df"]
			new_table = inflection_table_df_filtered
			old_range = inflection_tables_dict[inflection_name]["range"]
			new_range = cell_range
			old_like = inflection_tables_dict[inflection_name]["like"]
			new_like = like
			
			if (not old_table.equals(new_table)
			or old_range != new_range
			or old_like != new_like):
				print(f"{timeis()} {red}{inflection_name} changed {white}updated")
				inflection_tables_dict[inflection_name]["df"] = inflection_table_df_filtered
				inflection_tables_dict[inflection_name]["range"] = cell_range
				inflection_tables_dict[inflection_name]["like"] = like
				pattern_changed.append(inflection_name)

		except:
			print(f"{timeis()} {red}{inflection_name} doesn't exist {white}added")
			inflection_tables_dict[inflection_name] = {}
			inflection_tables_dict[inflection_name]["df"] = inflection_table_df_filtered
			inflection_tables_dict[inflection_name]["range"] = cell_range
			inflection_tables_dict[inflection_name]["like"] = like
			pattern_changed.append(inflection_name)

	print(f"{timeis()} {green}test if inflection table exists")
	
	pattern_deleted = []
	for inflection in inflection_tables_dict:
		if inflection not in inflection_table_index_dict:
			print(f"{timeis()} {red}{inflection} no longer exists {white}deleted")
			pattern_deleted.append(inflection)

	for deleted in pattern_deleted:
		inflection_tables_dict.pop(deleted)
		
	with open("output/inflection tables dict", "wb") as f:
		pickle.dump(inflection_tables_dict, f)

	with open (f"../frequency maps/output/pickle tests/pattern_changed", "wb") as pattern_changed_pickle:
			pickle.dump(pattern_changed, pattern_changed_pickle)


def create_dpd_df():
	print(f"{timeis()} {green}creating dpd dataframe")
	
	global dpd_df
	
	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)

	global dpd_df_length
	dpd_df_length = dpd_df.shape[0]

	global headwords_list
	headwords_list = dpd_df["Pāli1"].tolist()


def import_old_inflections_dict():
	print(f"{timeis()} {green}importing old inflections dict")

	global old_inflections_dict

	with open("output/all inflections dict", "rb") as f:
		old_inflections_dict = pickle.load(f)
	

def test_for_missing_stem_and_pattern():
	print(f"{timeis()} {green}test for missing stems and patterns")

	error = False
	missing_stem_string = ""
	missing_pattern_string = ""

	for row in range(dpd_df_length):
		headword = dpd_df.loc[row, "Pāli1"]
		stem = dpd_df.loc[row, "Stem"]
		pattern = dpd_df.loc[row, "Pattern"]

		if stem == "":
			missing_stem_string += headword + "|"
			error = True

		if stem != "-" and pattern == "":
			missing_pattern_string += headword + "|"
			error = True

	if missing_stem_string != "":
		print(f"{timeis()} {red}words with missing stems: {missing_stem_string}")
	if missing_pattern_string != "":
		print(f"{timeis()} {red}words with missing patterns: {missing_pattern_string}")
	if error == True:
		input(f"{timeis()} {red}there are stem & pattern errors, please fix them before continuing")


def test_for_wrong_patterns():

	print(f"{timeis()} {green}testing for wrong patterns")

	index_patterns = inflection_table_index_df["inflection name"].values.tolist()
	error = False
	wrong_patten_string = ""

	for row in range(dpd_df_length):
		headword =  dpd_df.loc[row, "Pāli1"]
		stem = dpd_df.loc[row, "Stem"]
		pattern = dpd_df.loc[row, "Pattern"]

		if stem == "-":
			pass
		elif stem == "!":
			pass
		elif pattern in index_patterns:
			pass
		elif pattern not in index_patterns:
			wrong_patten_string += headword + "|"
			error = True
		else:
			pass

	if wrong_patten_string != "":
		print(f"{timeis()} {red}wrong patterns: {wrong_patten_string}")
	if error == True:
		print(f"{timeis()} {red}wrong patterns - fix 'em!")


def test_for_differences_in_stem_and_pattern():

	print(f"{timeis()} {green}testing for changes in stem and pattern")

	global changed_headwords
	changed_headwords = set()

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		stem = dpd_df.loc[row, "Stem"]
		pattern = dpd_df.loc[row, "Pattern"]

		if pattern in pattern_changed:
			changed_headwords.add(headword)
	
		try:

			if old_inflections_dict[headword]["stem"] != stem:
				print(f"{timeis()} {white}{headword} stem {stem} changed")
				changed_headwords.add(headword)
				
			if old_inflections_dict[headword]["pattern"] != pattern:
				print(f"{timeis()} {white}{headword} pattern {pattern} changed")
				changed_headwords.add(headword)
		
		except:
			print(f"{timeis()} {white}{headword} not found")
			changed_headwords.add(headword)

	with open("../frequency maps/output/pickle tests/stem_pattern_differences", "wb") as f:
		pickle.dump(changed_headwords, f)

def test_for_missing_html():
	print(f"{timeis()} {green}testing for missing html files")

	for headword in headwords_list:
		if headword not in changed_headwords:
			try:
				open(f'output/html tables/{headword}.html')
			except:
				print(f"{timeis()} {red}{headword} missing html file")
				changed_headwords.add(headword)


def generate_all_inflections_dict():
	
	print(f"{timeis()} {green}generating all inflections dict")

	global all_inflections_dict
	all_inflections_dict = {}

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		pos = dpd_df.loc[row, "POS"]
		stem = dpd_df.loc[row, "Stem"]
		stem_clean = stem
		# stem contains "!.+" - must get inflection table but no synonsyms
		if re.match("!.+", stem) != None:
			stem = "!"
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]
		buddhadatta = dpd_df.loc[row, "Buddhadatta"]
		literal = dpd_df.loc[row, "Literal Meaning"]
		source1 = dpd_df.loc[row, "Source1"]
		sutta1 = dpd_df.loc[row, "Sutta1"]
		example1 = dpd_df.loc[row, "Example1"]
		source2 = dpd_df.loc[row, "Source 2"]
		sutta2 = dpd_df.loc[row, "Sutta2"]
		example2 = dpd_df.loc[row, "Example 2"]

		if literal != "":
			meaning += "; lit. " + literal
	
		if row % 5000 == 0:
			print(f"{timeis()} {row}/{len(dpd_df)}\t{headword}")
		
		if stem == "-":
			all_inflections_dict.update(
				{headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala": "", "devanagari": "", "thai": ""}})

		elif stem == "!":
			all_inflections_dict.update(
				{headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala": "", "devanagari": "", "thai": ""}})

		else:
			all_inflections_dict.update(
				{headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala": "", "devanagari": "", "thai": ""}})

			try:
				df = inflection_tables_dict[pattern]["df"]
				# df = pd.read_csv(f"output/patterns/{pattern}.csv", sep="\t", header=None)
				df.fillna("", inplace=True)
				df_rows = df.shape[0]
				df_columns = df.shape[1]

				for rows in range(1, df_rows):
					for columns in range(1, df_columns, 2):
						line = df.iloc[rows, columns]
						line = re.sub(r"(.+)", f"{stem}\\1", line)
						search_string = re.compile("\n", re.M)
						replace_string = " "
						matches = re.sub(search_string, replace_string, line).split(" ")
						for match in matches:
							if match != '':
								all_inflections_dict[headword]["inflections"].add(match)

			except:
				with open("inflection generator errorlog.txt", "a") as error_log:
					print(f"{timeis()} {red}error on: {headword}")
			
			if (
			source1 != "" and
			sutta1 != "" and
			example1 != ""):
				all_inflections_dict[headword]["sutta1"] = True
			else:
				all_inflections_dict[headword]["sutta1"] = False

			if (
			source2 != "" and
			sutta2 != "" and
			example2 != ""):
				all_inflections_dict[headword]["sutta2"] = True
			else:
				all_inflections_dict[headword]["sutta2"] = False


	df = pd.DataFrame.from_dict(all_inflections_dict, orient='index')
	df.to_csv("output/all inflections dict.csv", sep="\t")
	with open("output/all inflections dict", "wb") as f:
		pickle.dump(all_inflections_dict, f)
	

def update_all_inflections_dict():

	print(f"{timeis()} {green}updating all inflections dict")

	global all_inflections_dict
	all_inflections_dict = old_inflections_dict

	old_headwords_set = set(old_inflections_dict.keys())
	new_headwords_set = set(dpd_df["Pāli1"].tolist())

	unused = old_headwords_set - new_headwords_set
	for headword in unused:
		all_inflections_dict.pop(headword)

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		pos = dpd_df.loc[row, "POS"]
		stem = dpd_df.loc[row, "Stem"]
		stem_clean = stem
		# stem contains "!.+" - must get inflection table but no synonsyms
		if re.match("!.+", stem) != None:
			stem = "!"
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]
		buddhadatta = dpd_df.loc[row, "Buddhadatta"]
		literal = dpd_df.loc[row, "Literal Meaning"]
		source1 = dpd_df.loc[row, "Source1"]
		sutta1 = dpd_df.loc[row, "Sutta1"]
		example1 = dpd_df.loc[row, "Example1"]
		source2 = dpd_df.loc[row, "Source 2"]
		sutta2 = dpd_df.loc[row, "Sutta2"]
		example2 = dpd_df.loc[row, "Example 2"]

		if literal != "":
			meaning += "; lit. " + literal

		if headword not in changed_headwords:
			
			try:
				all_inflections_dict[headword]["meaning"] = meaning
			except:
				print(f"{timeis()} {red}{headword} - error adding meaning")

			try:
				all_inflections_dict[headword]["meaning2"] = buddhadatta
			except:
				print(f"{timeis()} {red}{headword} - error adding meaning2")

			try:
				all_inflections_dict[headword]["pos"] = pos
			except:
				print(f"{timeis()} {red}{headword} - error adding pos")

			if (
			source1 != "" and
			sutta1 != "" and
			example1 != ""):
				all_inflections_dict[headword]["sutta1"] = True
			else:
				all_inflections_dict[headword]["sutta1"] = False

			if (
			source2 != "" and
			sutta2 != "" and
			example2 != ""):
				all_inflections_dict[headword]["sutta2"] = True
			else:
				all_inflections_dict[headword]["sutta2"] = False		


		if headword in changed_headwords:
			print(f"{timeis()} {row}/{len(dpd_df)}\t{headword}")
			
			if stem == "-":
				all_inflections_dict.update({headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala":"", "devanagari":"", "thai":""}})
			
			elif stem == "!":
				all_inflections_dict.update({headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala":"", "devanagari":"", "thai":""}})
			
			else:
				all_inflections_dict.update({headword: {"pos": pos, "meaning": meaning, "meaning2": buddhadatta, "stem": stem_clean, "pattern": pattern, "inflections": {headword_clean}, "sinhala": "", "devanagari": "", "thai": ""}})
				
				try:
					df_table = inflection_tables_dict[pattern]["df"].copy()
					# df = pd.read_csv(f"output/patterns/{pattern}.csv", sep="\t", header=None)
					df_table.fillna("", inplace=True)
					df_rows = df_table.shape[0]
					df_columns = df_table.shape[1]

					for rows in range(0, df_rows):
						for columns in range(0, df_columns, 2):
							line = df_table.iloc[rows, columns]
							line = re.sub(r"(.+)", f"{stem}\\1", line)
							search_string = re.compile("\n", re.M)
							replace_string = " "
							matches = re.sub(search_string, replace_string, line).split(" ")
							for match in matches:
								if match != '':
									all_inflections_dict[headword]["inflections"].add(match)

				except:
					with open("inflection generator errorlog.txt", "a") as error_log:
						print(f"{timeis()} {red}error on: {headword}")

			if (
			source1 != "" and
			sutta1 != "" and
			example1 != ""):
				all_inflections_dict[headword]["sutta1"] = True
			else:
				all_inflections_dict[headword]["sutta1"] = False

			if (
			source2 != "" and
			sutta2 != "" and
			example2 != ""):
				all_inflections_dict[headword]["sutta2"] = True
			else:
				all_inflections_dict[headword]["sutta2"] = False

	df = pd.DataFrame.from_dict(all_inflections_dict, orient='index')
	df.to_csv("output/all inflections dict.csv", sep="\t")
	with open("output/all inflections dict", "wb") as f:
		pickle.dump(all_inflections_dict, f)


def generate_html_inflection_table():
	print(f"{timeis()} {green}generating html inflection tables")

	indeclinables = ["abbrev", "abs", "ger", "ind", "inf", "prefix"]
	conjugations = ["aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"]
	declensions = ["adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron", "prp", "ptp", "root", "suffix", "ve"]

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None: #stem contains "!.+" - must get inflection table but no synonsyms
			stem = re.sub("!", "", stem)
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]

		if headword in changed_headwords:
			print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")

			html_file = open(f"output/html tables/{headword}.html", "w")
				
			if stem == "-":
				html_file.write(f"<p><b>{headword_clean}</b> is indeclinable")

			elif stem == "!":
				html_file.write(f"<p>click on <b>{pattern}</b> for inflection table")

			else:
				df_table = inflection_tables_dict[pattern]["df"].copy()
				# df = pd.read_csv(f"output/patterns/{pattern}.csv", sep="\t", index_col=0)
				df_table.fillna("", inplace=True)
				df_rows = df_table.shape[0]
				df_columns = df_table.shape[1]

				for rows in range(0, df_rows): 
					for columns in range(0, df_columns, 2): #1 to 0
						html_cell = df_table.iloc[rows, columns]
						html_cell = re.sub(r"(.+)", f"<b>\\1</b>", html_cell) # add bold
						html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell) # add stem
						html_cell = re.sub(r"\n", "<br>", html_cell) # add line breaks
						df_table.iloc[rows, columns] = html_cell

				column_list = []
				for i in range(1, df_columns, 2):
					column_list.append(i)

				df_table.drop(df_table.columns[column_list], axis=1, inplace=True)
				html_table = df_table.to_html(escape=False)
				html_table = re.sub("Unnamed.+", "", html_table)
				html_table = re.sub("NaN", "", html_table)

				# write header info

				if inflection_table_index_dict[pattern] != "":
					if pos in declensions:
						heading = (f"""<p class ="heading"><b>{headword_clean}</b> is <b>{pattern}</b> declension like <b>{inflection_table_index_dict[pattern]}</b></p>""")
					if pos in conjugations:
						heading = (f"""<p class ="heading"><b>{headword_clean}</b> is <b>{pattern}</b> conjugation like <b>{inflection_table_index_dict[pattern]}</b></p>""")

				if inflection_table_index_dict[pattern] == "":
					if pos in declensions:
						heading = (f"""<p class ="heading"><b>{headword_clean}</b> is <b>{pattern}</b> irregular declension</p>""")
					if pos in conjugations:
						heading = (f"""<p class ="heading"><b>{headword_clean}</b> is <b>{pattern}</b> irregular conjugation</p>""")
			
				html = heading + html_table 
				html_file.write(html)

def transliterate_inflections():

	print(f"{timeis()} {green}transliterating inflections to sinhala devanagari thai")

	length = (len(all_inflections_dict))
	counter = 0

	for headword in all_inflections_dict:
		
		# # if changed or empty then add
		
		if headword in changed_headwords or \
		all_inflections_dict[headword]["sinhala"] == "":

			inflections_string = ""
		
			print(f"{timeis()} {counter}/{length} {headword}")

			inflections = all_inflections_dict[headword]["inflections"]
			for inflection in inflections:
				inflections_string += inflection + " "
			
			sinhala = transliterate.process("IASTPali", "Sinhala", inflections_string, post_options=['SinhalaPali', 'SinhalaConjuncts'])
			all_inflections_dict[headword]["sinhala"] = set(sinhala.split(" "))

			devanagari = devanagari = transliterate.process("IASTPali", "Devanagari", inflections_string, post_options=['DevanagariAnusvara'])
			all_inflections_dict[headword]["devanagari"] = set(devanagari.split(" "))

			thai = transliterate.process("IASTPali", "Thai", inflections_string)
			all_inflections_dict[headword]["thai"] = set(thai.split(" "))

		counter +=1

	df = pd.DataFrame.from_dict(all_inflections_dict, orient='index')
	df.to_csv("output/all inflections dict.csv", sep="\t")
	with open("output/all inflections dict", "wb") as f:
		pickle.dump(all_inflections_dict, f)


def delete_unused_html_tables():
	print(f"{timeis()} {green}deleting unused html files ")

	for root, dirs, files in os.walk("output/html tables", topdown=True):
		for file in files:
			try:
				file_clean = re.sub(".html", "", file)
				if file_clean not in headwords_list:
					os.remove(f"output/html tables/{file}")
					print(f"{timeis()} {file}")
			except:
				print(f"{timeis()} {red}{file} not found")


def generate_grammar_dict():

	print(f"{timeis()} {green}generating grammar df from scratch")


	grammar_dict = {}

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None:
			stem = re.sub("!.+", "!", stem)
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]

		if row % 5000 == 0:
			print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")

		if stem == "-":
			grammar_dict[headword] = {'inflection':{headword_clean: f'<b>{headword_clean}</b> is <b>indeclineable</b> ({pos})'}}

		elif stem == "!":
			pass

		else:
			df_table = inflection_tables_dict[pattern]["df"].copy()
			df_table.fillna("", inplace=True)
			df_rows = df_table.shape[0]
			df_columns = df_table.shape[1]

			for rows in range(0, df_rows):
				for columns in range(0, df_columns, 2):  # 1 to 0
					html_cell = df_table.iloc[rows, columns]
					html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell)  # add stem
					df_table.iloc[rows, columns] = html_cell

			column_list = []
			for i in range(0, df_columns, 2):
				column_list.append(i)

			try:
				df_table.drop(index="in comps", inplace=True)
			except:
				pass

			for column in column_list:
				for row in range(len(df_table)):
					inflections = df_table.iloc[row, column].split("\n")
					grammar = df_table.iloc[row, column+1]

					for inflection in inflections:
						if inflection != "":
							data_row = f"<b>{inflection}</b> is <b>{grammar}</b> of {headword_clean} ({pos})"

							try:
								if inflection in grammar_dict[headword][inflection]:
									grammar_dict[headword] = {'inflection':{inflection:data_row}}
									data_row_escaped = re.escape(data_row)
									if not re.findall(data_row_escaped, grammar_dict[headword][inflection]):
										grammar_dict[headword][inflection] += f"<br>{data_row}"
							
							except:
								grammar_dict[headword] = {'inflection': {inflection: data_row}}


	grammar_df = pd.DataFrame.from_dict(grammar_dict, orient='index')
	grammar_df.to_csv("output/grammar df.csv", sep="\t", index=None)
	with open('output/grammardict', 'wb') as p:
		pickle.dump(grammar_dict, p)



def update_grammar_dict():
	print(f"{timeis()} {green}updating grammar dict")

	with open('output/grammardict', 'rb') as p:
		grammar_dict = pickle.load(p) 

	for headword in changed_headwords:
		grammar_dict.pop(headword)
	
	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]

		if headword in changed_headwords:
			headword_clean = re.sub(" \d*$", "", headword)
			stem = dpd_df.loc[row, "Stem"]
			if re.match("!.+", stem) != None:
				stem = re.sub("!.+", "!", stem)
			if stem == "*":
				stem = ""
			pattern = dpd_df.loc[row, "Pattern"]
			pos = dpd_df.loc[row, "POS"]

			if row % 5000 == 0:
				print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")

			if stem == "-":
				grammar_dict[headword] = {'inflection': {
					headword_clean: f'<b>{headword_clean}</b> is <b>indeclineable</b> ({pos})'}}

			elif stem == "!":
				pass

			else:
				df_table = inflection_tables_dict[pattern]["df"].copy()
				df_table.fillna("", inplace=True)
				df_rows = df_table.shape[0]
				df_columns = df_table.shape[1]

				for rows in range(0, df_rows):
					for columns in range(0, df_columns, 2):  # 1 to 0
						html_cell = df_table.iloc[rows, columns]
						html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell)  # add stem
						df_table.iloc[rows, columns] = html_cell

				column_list = []
				for i in range(0, df_columns, 2):
					column_list.append(i)

				try:
					df_table.drop(index="in comps", inplace=True)
				except:
					pass

				for column in column_list:
					for row in range(len(df_table)):
						inflections = df_table.iloc[row, column].split("\n")
						grammar = df_table.iloc[row, column+1]

						for inflection in inflections:
							if inflection != "":
								data_row = f"<b>{inflection}</b> is <b>{grammar}</b> of {headword_clean} ({pos})"

								try:
									if inflection in grammar_dict[headword][inflection]:
										grammar_dict[headword] = {'inflection': {inflection: data_row}}
										data_row_escaped = re.escape(data_row)
										if not re.findall(data_row_escaped, grammar_dict[headword][inflection]):
											grammar_dict[headword][inflection] += f"<br>{data_row}"

								except:
									grammar_dict[headword] = {'inflection': {inflection: data_row}}

	grammar_df = pd.DataFrame.from_dict(grammar_dict, orient='index')
	grammar_df.to_csv("output/grammar df.csv", sep="\t", index=None)
	with open('output/grammardict', 'wb') as p:
		pickle.dump(grammar_dict, p)

def reformat_gramma_dict():
	print(f"{timeis()} {green}reformatting grammar dict")
	


def make_grammar_dict():
	print(f"{timeis()} {green}making grammar dict")
	grammar_df_len = len(grammar_df)
	grammar_dict = {}

	for row in range(grammar_df_len):
		inflection = grammar_df.iloc[row, 0]
		grammar = grammar_df.iloc[row, 1]
		headword = grammar_df.iloc[row, 2]
		headword_clean = re.sub(" \d*$", "", headword)
		pos = grammar_df.iloc[row, 3]

		if row % 5000 == 0:
			print(f"{timeis()} {row}/{grammar_df_len}\t{inflection}")

		if grammar == "indeclineable":
			data_row = f"<b>{inflection}</b> is <b>indecliable</b> ({pos})" 
		
		else:
			data_row = f"<b>{inflection}</b> is <b>{grammar}</b> of {headword_clean} ({pos})"
		
		if inflection not in grammar_dict.keys():
			grammar_dict[inflection] = data_row
		
		elif inflection in grammar_dict.keys():
			if not re.findall(data_row, grammar_dict[inflection]):
				grammar_dict[inflection] += f"<br>{data_row}"

	grammar_data_list = []
	for key, value in grammar_dict.items():
		grammar_data_list += [[f"{key}", f"""{value}""", "", ""]]

	grammar_data_df = pd.DataFrame(grammar_data_list)
	grammar_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]
	grammar_data_df.to_csv('output/grammar for dict.csv', sep='\t', index=None)
	return grammar_data_df




# make some compact data
# make gd
# made mdict

# from here on its for sutta colouring
# fixme split into another module?


def make_list_of_all_inflections():
	print(f"{timeis()} {green}creating all inflections df")

	global all_inflections_df
	all_inflections_df = pd.read_csv("output/all inflections.csv", header=None, sep="\t")

	print(f"{timeis()} making master list of all inflections")

	# global all_inflections_list
	all_inflections_string = ""
	all_inflections_length = all_inflections_df.shape[0]
	for row in range (all_inflections_length):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]
		all_inflections_string += inflections
		
		if row %5000 == 0:
			print(f"{timeis()} {row}/{all_inflections_length}\t{headword}")

	all_inflections_list = all_inflections_string.split()
	all_inflections_list = list(dict.fromkeys(all_inflections_list))

	global all_inflections_set
	all_inflections_set = set(dict.fromkeys(all_inflections_list))

	# with open(f"output/all inflections list", "wb") as p:
	# 	pickle.dump(all_inflections_set, p)


def make_list_of_all_inflections_no_meaning():

	print(f"{timeis()} {green}making list of all inflections with no meaning")

	global no_meaning_list

	test1 = dpd_df["Meaning IN CONTEXT"] != ""
	test2 = dpd_df["POS"] != "prefix"
	test3 = dpd_df["POS"] != "suffix"
	test4 = dpd_df["POS"] != "cs"
	test5 = dpd_df["POS"] != "ve"
	test6 = dpd_df["POS"] != "idiom"
	filter = test1 & test2 & test3 & test4 & test5 & test6

	no_meaning_df = dpd_df[filter]

	no_meaning_headword_list = no_meaning_df["Pāli1"].tolist()

	no_meaning_df = all_inflections_df[all_inflections_df[0].isin(no_meaning_headword_list)]

	no_meaning_string = ""
	all_inflections_length = all_inflections_df.shape[0]
	for row in range (all_inflections_length):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]


		if row %5000 == 0:
			print(f"{timeis()} {row}/{all_inflections_length}\t{headword}")

		if headword in no_meaning_headword_list:
			no_meaning_string += inflections

	no_meaning_list = no_meaning_string.split()
	no_meaning_list = list(dict.fromkeys(no_meaning_list))


def make_list_of_all_inflections_no_eg1():
	print(f"{timeis()} {green}making list of all inflections with no eg1")

	global no_eg1_list

	test = dpd_df["Sutta1"] == ""
	no_eg1_df = dpd_df[test]

	no_eg1_headword_list = no_eg1_df["Pāli1"].tolist()

	no_eg1_df = all_inflections_df[all_inflections_df[0].isin(no_eg1_headword_list)]

	no_eg1_string = ""
	all_inflections_length = all_inflections_df.shape[0]
	for row in range (all_inflections_length):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]

		if row %5000 == 0:
			print(f"{timeis()} {row}/{all_inflections_length}\t{headword}")

		if headword in no_eg1_headword_list:
			no_eg1_string += inflections

	no_eg1_list = no_eg1_string.split()
	no_eg1_list = list(dict.fromkeys(no_eg1_list))


def make_list_of_all_inflections_no_eg2():

	print(f"{timeis()} {green}making list of all inflections with no eg2")

	global no_eg2_list

	test = dpd_df["Sutta2"] == ""
	no_eg2_df = dpd_df[test]

	no_eg2_headword_list = no_eg2_df["Pāli1"].tolist()

	no_eg2_df = all_inflections_df[all_inflections_df[0].isin(no_eg2_headword_list)]

	no_eg2_string = ""
	all_inflections_length = all_inflections_df.shape[0]
	for row in range (all_inflections_length):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]

		if row %5000 == 0:
			print(f"{timeis()} {row}/{all_inflections_length}\t{headword}")

		if headword in no_eg2_headword_list:
			no_eg2_string += inflections

	no_eg2_list = no_eg2_string.split()
	no_eg2_list = list(dict.fromkeys(no_eg2_list))

def clean_machine(text):
	text = text.lower()
	text = re.sub("\d", "", text)
	text = re.sub("\.", " ", text) #sometmes no space afterwards, so needs space
	text = re.sub(",", " ", text)
	text = re.sub(";", " ", text)
	text = re.sub("‘", "", text)
	text = re.sub("’", "", text)
	text = re.sub("`", "", text)
	text = re.sub("!", "", text)	
	text = re.sub("\?", "", text)
	text = re.sub("\+", "", text)
	text = re.sub("=", "", text)	
	text = re.sub("﻿", "", text)
	text = re.sub("§", " ", text)
	text = re.sub("\(", " ", text)
	text = re.sub("\)", " ", text)
	text = re.sub("-", " ", text)
	text = re.sub("–", "", text)	
	text = re.sub("\t", " ", text)
	text = re.sub("…", " ", text)
	text = re.sub("–", "", text)
	text = re.sub("\n", " \n ", text)
	text = re.sub("  ", " ", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	text = re.sub("॰", "", text)
	text = re.sub("ï", "i", text)
	text = re.sub("ü", "u", text)
	
	return text

def read_and_clean_sutta_text():

	print(f"{timeis()} {green}reading and cleaning sutta file")

	global sutta_file
	global commentary_file
	global sub_commentary_file
	
	global input_path
	input_path = "../pure-machine-readable-corpus/cscd/"

	global output_path
	output_path = "output/html suttas/"

	sutta_dict = pd.read_csv('sutta corespondence tables/sutta correspondence tables.csv', sep="\t", index_col=0, squeeze=True).to_dict(orient='index',)

	while True:
		sutta_number = input (f"{timeis()} enter sutta number:{blue} ")
		if sutta_number in sutta_dict.keys():
			sutta_file = sutta_dict.get(sutta_number).get("mūla")
			commentary_file = sutta_dict.get(sutta_number).get("aṭṭhakathā")
			sub_commentary_file = sutta_dict.get(sutta_number).get("ṭīkā")
			break
		elif sutta_number not in sutta_dict.keys():
			print(f"{timeis()} {red}sutta number not recognised, please try again")
			continue

	with open(f"{input_path}{sutta_file}", 'r') as input_file :
		sutta_text = input_file.read()

	sutta_text = clean_machine(sutta_text)

	with open(f"{output_path}{sutta_file}", "w") as output_file:
		output_file.write(sutta_text)

	# commentary

	with open(f"{input_path}{commentary_file}", 'r') as input_file :
		commentary_text = input_file.read()

	commentary_text = clean_machine(commentary_text)

	with open(f"{output_path}{commentary_file}", "w") as output_file:
		output_file.write(commentary_text)

def make_comparison_table():

	print(f"{timeis()} {green}making sutta comparison table")

	with open(f"{output_path}{sutta_file}") as text_to_split:
		word_llst=[word for line in text_to_split for word in line.split(" ")]

	global sutta_words_df
	sutta_words_df = pd.DataFrame(word_llst)

	inflection_test = sutta_words_df[0].isin(all_inflections_set)
	sutta_words_df["Inflection"] = inflection_test

	no_meaning_test = sutta_words_df[0].isin(no_meaning_list)
	sutta_words_df["Meaning"] = no_meaning_test

	eg1_test = sutta_words_df[0].isin(no_eg1_list)
	sutta_words_df["Eg1"] = ~eg1_test
	
	eg2_test = sutta_words_df[0].isin(no_eg2_list)
	sutta_words_df["Eg2"] = ~eg2_test

	sutta_words_df.rename(columns={0 :"Pali"}, inplace=True)

	sutta_words_df.drop_duplicates(subset=["Pali"], keep="first", inplace=True)

	with open(f"{output_path}{sutta_file}.csv", 'w') as txt_file:
		sutta_words_df.to_csv(txt_file, header=True, index=True, sep="\t")

	print(f"{timeis()} {green}making commentary comparison table")

	with open(f"{output_path}{commentary_file}") as text_to_split:
		word_llst=[word for line in text_to_split for word in line.split(" ")]

	global commentary_words_df
	commentary_words_df = pd.DataFrame(word_llst)

	inflection_test = commentary_words_df[0].isin(all_inflections_set)
	commentary_words_df["Inflection"] = inflection_test

	no_meaning_test = commentary_words_df[0].isin(no_meaning_list)
	commentary_words_df["Meaning"] = no_meaning_test
	
	commentary_words_df.rename(columns={0 :"Pali"}, inplace=True)

	commentary_words_df.drop_duplicates(subset=["Pali"], keep="first", inplace=True)

	with open(f"{output_path}{commentary_file}.csv", 'w') as txt_file:
		commentary_words_df.to_csv(txt_file, header=True, index=True, sep="\t")


def html_find_and_replace():

	print(f"{timeis()} {green}finding and replacing sutta html")

	global sutta_text
	global commentary_text

	no_meaning_string = ""
	no_eg1_string = ""
	no_eg2_string = ""

	with open(f"{output_path}{sutta_file}", 'r') as input_file:
		sutta_text = input_file.read()

	sandhi_df = pd.read_csv(
		"output/sandhi/matches_df.csv", sep="\t", dtype=str)
	
	max_row = sutta_words_df.shape[0]
	row=0

	for word in range(row, max_row):
		pali_word = str(sutta_words_df.iloc[row, 0])
		inflection_exists = str(sutta_words_df.iloc[row, 1])
		meaning_exists = str(sutta_words_df.iloc[row, 2])
		eg1_exists = str(sutta_words_df.iloc[row, 3])
		eg2_exists = str(sutta_words_df.iloc[row, 4])

		if row % 250 == 0:
			print(f"{timeis()} {row}/{max_row}\t{pali_word}")

		row +=1

		if meaning_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "highlight">\\2</span>\\3""", sutta_text)
			no_meaning_string += pali_word + " "

		elif eg1_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "orange">\\2</span>\\3""", sutta_text)
			no_eg1_string += pali_word + " "

		elif eg2_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "red">\\2</span>\\3""", sutta_text)
			no_eg2_string += pali_word + " "
		
	sutta_text = re.sub("\n", "<br><br>", sutta_text)
	sutta_text += "<br><br>" + 'no meanings: <span class = "highlight">' + no_meaning_string + "</span>"
	sutta_text += "<br><br>" + 'no eg1: <span class = "orange">' + no_eg1_string + "</span>"
	sutta_text += "<br><br>" + 'no eg2: <span class = "red">' + no_eg2_string + "</span>"

	print(f"{timeis()} {green}finding and replacing sutta sandhi")

	for row in range(len(sandhi_df)):
		sandhi = sandhi_df.loc[row, "word"]
		construction = sandhi_df.loc[row, "split"]
		construction = re.sub("[|]", "", construction)
		construction = re.sub("'", "", construction)

		if row % 250 == 0:
			print(f"{timeis()} {row}/{len(sandhi_df)}\t{sandhi}")

		sutta_text = re.sub(fr"(^|\s|<|>)({sandhi})(<|>|\s|\n|$)", f"""\\1<abbr title="{construction}">\\2</abbr>\\3""", sutta_text)

	print(f"{timeis()} {green}finding and replacing commentary html")

	no_meaning_string = ""
	no_inflection_string = ""

	with open(f"{output_path}{commentary_file}", 'r') as input_file:
		commentary_text = input_file.read()
	
	max_row = commentary_words_df.shape[0]
	row=0

	for word in range(row, max_row):
		pali_word = str(commentary_words_df.iloc[row, 0])
		inflection_exists = str(commentary_words_df.iloc[row, 1])
		meaning_exists = str(commentary_words_df.iloc[row, 2])

		if row % 250 == 0:
			print(f"{timeis()} {row}/{max_row}\t{pali_word}")

		row +=1

		if inflection_exists == "False":

			commentary_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "highlight">\\2</span>\\3""", commentary_text)
			no_inflection_string += pali_word + " "

		elif meaning_exists == "False":

			commentary_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "orange">\\2</span>\\3""", commentary_text)
			no_meaning_string += pali_word + " "

	commentary_text = re.sub("\n", "<br><br>", commentary_text)
	commentary_text += "<br><br>" + 'no inflection: <span class = "highlight">' + no_inflection_string + "</span>"
	commentary_text += "<br><br>" + 'no meanings: <span class = "orange">' + no_meaning_string + "</span>"

	print(f"{timeis()} {green}finding and replacing commentary sandhi")

	for row in range(len(sandhi_df)):
		sandhi = sandhi_df.loc[row, "word"]
		construction = sandhi_df.loc[row, "split"]
		construction = re.sub("[|]", "", construction)
		construction = re.sub("'", "", construction)

		if row % 250 == 0:
			print(f"{timeis()} {row}/{len(sandhi_df)}\t{sandhi}")

		commentary_text = re.sub(fr"(^|\s|<|>)({sandhi})(<|>|\s|\n|$)", f"""\\1<abbr title="{construction}">\\2</abbr>\\3""", commentary_text)



def write_html():
	print(f"{timeis()} {green}writing html file")
	
	html1 = """
<!DOCTYPE html>
<html>
<head>
<style>
#content, html, body { 
	height: 98%;
	font-size: 1.2em;
	}

#left {
    float: left;
    width: 50%;
    height: 100%;
    overflow: scroll;}

#right {
    float: left;
    width: 50%;
    height: 100%;
	overflow: scroll;
	}

body {
	color: #3b2e18;
	background-color: #221a0e;
	}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
	}

::-webkit-scrollbar-button {
    width: 0px;
    height: 0px;
	}

::-webkit-scrollbar-thumb {
    background: #46351d;
    border: 2px solid transparent;
    border-radius: 10px;
	}

::-webkit-scrollbar-thumb:hover {
    background: #9b794b;
	}

::-webkit-scrollbar-track:hover {
    background: transparent;
	}

::-webkit-scrollbar-thumb:active {
    background: #9b794b;
	}

::-webkit-scrollbar-track:active {
    background: #332715;
	}

::-webkit-scrollbar-track {
    background: transparent;
    border: 0px none transparent;
    border-radius: 10px;
	}

::-webkit-scrollbar-corner {
    background: transparent;
	border-radius: 10px;
	}

.highlight {
	color:#feffaa;
	}

.red{
    border-radius: 5px;
    color: #c22b45;
	}

.orange{
    border-radius: 5px;
    color: #d7551b;
	}

</style>
</head>
<body>
<div id="content">
<div id="left">"""

	html2 = """</div><div id="right">"""

	html3 = """</div></div>"""

	with open (f"{output_path}{sutta_file}.html", "w") as html_file:
		html_file.write(html1)
		html_file.write(sutta_text)
		html_file.write(html2)
		html_file.write(commentary_text)
		html_file.write(html3)
		html_file.close

