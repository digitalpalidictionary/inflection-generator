#!/usr/bin/env python3
# coding: utf-8

from timeis import timeis, yellow, line, white, green, tic, toc
import json
import pandas as pd
import re
import pickle

from subprocess import check_output
from aksharamukha import transliterate
from timeis import timeis, blue, yellow, green, red, white, line
from delete_unused_files import del_unused_files


def create_inflection_table_index():

	print(f"{timeis()} {yellow}inflection generator")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}creating inflection table index")

	inflection_table_index_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="index", dtype=str)

	inflection_table_index_df.fillna("", inplace=True)

	inflection_table_index_length = len(inflection_table_index_df)

	inflection_table_index_dict = dict(zip(inflection_table_index_df.iloc[:, 0], inflection_table_index_df.iloc[:, 2]))

	return inflection_table_index_df, inflection_table_index_length, inflection_table_index_dict


def generate_inflection_tables_dict(
	inflection_table_index_df,
	inflection_table_index_length
	):

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

		col_range_1 = re.sub("(.+?)\\d*\\:.+", "\\1", cell_range)
		col_range_2 = re.sub(".+\\:(.[A-Z]*)\\d*", "\\1", cell_range)
		row_range_1 = int(re.sub(".+?(\\d{1,3}):.+", "\\1", cell_range))
		row_range_2 = int(re.sub(".+:.+?(\\d{1,3})", "\\1", cell_range))

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
		inflection_table_df_filtered.rename_axis(None, axis=1, inplace=True) # delete pattern name

		inflection_tables_dict[inflection_name] = {}
		inflection_tables_dict[inflection_name]["df"] = inflection_table_df_filtered
		inflection_tables_dict[inflection_name]["range"] = cell_range
		inflection_tables_dict[inflection_name]["like"] = like
	
	with open("output/inflection tables dict", "wb") as f:
		pickle.dump(inflection_tables_dict, f)


def create_inflection_table_df():
	print(f"{timeis()} {green}creating inflection table dataframe")

	inflection_table_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="declensions", dtype=str)

	inflection_table_df = inflection_table_df.shift(periods=2)

	inflection_table_df.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK", "BL", "BM", "BN", "BO", "BP", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BX", "BY", "BZ", "CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM", "CN", "CO", "CP", "CQ", "CR", "CS", "CT", "CU", "CV", "CW", "CX", "CY", "CZ", "DA", "DB", "DC", "DD", "DE", "DF", "DG", "DH", "DI", "DJ", "DK"]

	inflection_table_df.fillna("", inplace=True)

	return inflection_table_df


def test_inflection_pattern_changed(
	inflection_table_index_df, 
	inflection_table_index_length,
	inflection_table_index_dict,
	inflection_table_df
	):

	print(f"{timeis()} {green}test if inflection table has changed")
	
	with open("output/inflection tables dict", "rb") as f:
		inflection_tables_dict = pickle.load(f)

	pattern_changed = []

	for row in range(inflection_table_index_length):
		inflection_name = inflection_table_index_df.iloc[row,0]
		cell_range = inflection_table_index_df.iloc[row,1]
		like = inflection_table_index_df.iloc[row,2]

		col_range_1 = re.sub("(.+?)\\d*\\:.+", "\\1", cell_range)
		col_range_2 = re.sub(".+\\:(.[A-Z]*)\\d*", "\\1", cell_range)
		row_range_1 = int(re.sub(".+?(\\d{1,3}):.+", "\\1", cell_range))
		row_range_2 = int(re.sub(".+:.+?(\\d{1,3})", "\\1", cell_range))

		inflection_table_df_filtered = inflection_table_df.loc[row_range_1:row_range_2, col_range_1:col_range_2]
		inflection_table_df_filtered.name = f"{inflection_name}"
		inflection_table_df_filtered.reset_index(drop=True, inplace=True)
		inflection_table_df_filtered.iloc[0,0] = ""

		# replace header
		new_header = inflection_table_df_filtered.iloc[0] #grab the first row for the header
		inflection_table_df_filtered = inflection_table_df_filtered[1:] #take the data less the header row
		inflection_table_df_filtered.columns = new_header #set the header row as the df header

		# replace index
		inflection_table_df_filtered.index = inflection_table_df_filtered.iloc[0:,0]
		inflection_table_df_filtered = inflection_table_df_filtered.iloc[:, 1:]
		inflection_table_df_filtered.rename_axis(None, axis=1, inplace=True) # delete pattern name

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

	with open (f"../frequency maps/output/pickle tests/pattern_changed", "wb") as p:
			pickle.dump(pattern_changed, p)

	return inflection_tables_dict, pattern_changed


def create_dpd_df():
	print(f"{timeis()} {green}creating dpd dataframe")
	
	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)

	dpd_df_length = dpd_df.shape[0]

	headwords_list = dpd_df["Pāli1"].tolist()

	return dpd_df, dpd_df_length, headwords_list


def import_old_inflections_dict():
	print(f"{timeis()} {green}importing old inflections dict")

	with open("output/all inflections dict", "rb") as f:
		old_inflections_dict = pickle.load(f)
	
	return old_inflections_dict

def import_allwords_set():
	with open ("output/allwords set", "rb") as p:
		allwords_set = pickle.load(p)
	return allwords_set

allwords_set = import_allwords_set()


def test_for_missing_stem_and_pattern(dpd_df, dpd_df_length):
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


def test_for_wrong_patterns(
	inflection_table_index_df,
	dpd_df,
	dpd_df_length
	):

	print(f"{timeis()} {green}testing for wrong patterns")

	index_patterns = inflection_table_index_df["inflection name"].values.tolist()
	error = False
	wrong_patten_string = ""

	for row in range(dpd_df_length):
		headword = dpd_df.loc[row, "Pāli1"]
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


def test_for_differences_in_stem_and_pattern(
	pattern_changed,
	dpd_df,
	dpd_df_length,
	old_inflections_dict
	):

	print(f"{timeis()} {green}testing for changes in stem and pattern")

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
	
	return changed_headwords


def test_for_missing_html(
	headwords_list,
	changed_headwords
	):

	print(f"{timeis()} {green}testing for missing html files")

	for headword in headwords_list:
		if headword not in changed_headwords:
			try:
				open(f'output/html tables/{headword}.html')
			except:
				print(f"{timeis()} {red}{headword} missing html file")
				changed_headwords.add(headword)

	with open("../frequency maps/output/pickle tests/stem_pattern_differences", "wb") as f:
		pickle.dump(changed_headwords, f)
	
	with open("output/changed headwords", "wb") as f:
		pickle.dump(changed_headwords, f)

	return changed_headwords


def generate_all_inflections_dict(
	inflection_tables_dict,
	dpd_df,
	dpd_df_length
	):
	
	print(f"{timeis()} {green}generating all inflections dict")

	all_inflections_dict = {}

	for row in range(dpd_df_length): # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \\d*$", "", headword)
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

				for rows in range(0, df_rows):
					for columns in range(0, df_columns, 2):
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
	with open("output/all inflections dict", "wb") as f:
		pickle.dump(all_inflections_dict, f)
	
	return all_inflections_dict
	

def update_all_inflections_dict(
	inflection_tables_dict,
	dpd_df,
	dpd_df_length,
	old_inflections_dict,
	changed_headwords
	):

	print(f"{timeis()} {green}updating all inflections dict")

	all_inflections_dict = old_inflections_dict

	old_headwords_set = set(old_inflections_dict.keys())
	new_headwords_set = set(dpd_df["Pāli1"].tolist())

	unused = old_headwords_set - new_headwords_set
	for headword in unused:
		if all_inflections_dict[headword]["pos"] != "sandhix": # sandhix gets checked later
			all_inflections_dict.pop(headword)

	for row in range(dpd_df_length): # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \\d*$", "", headword)
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
	
	return all_inflections_dict


def unused_patterns(
	inflection_table_index_df,
	dpd_df
	):

	print(f"{timeis()} {green}unused patterns")

	# list of all inflection patterns
	all_inflection_patterns = inflection_table_index_df["inflection name"].to_list()
	
	# list of all "aka" patterns
	aka_patterns = inflection_table_index_df["aka"].to_list()
	aka_patterns = sorted(set(aka_patterns))
	aka_patterns.remove("")

	# make a dict of all used patterns
	used_infl = {}
	for pattern in all_inflection_patterns:
		used_infl[pattern] = 0
	for pattern in aka_patterns:
		used_infl[pattern] = 0
	
	# count patterns used in dpd_df
	for row in range(len(dpd_df)):
		pattern = dpd_df.loc[row, "Pattern"]
		if pattern in used_infl:
			used_infl[pattern] += 1
	
	# print unused patterns
	for pattern in used_infl:
		if used_infl[pattern] == 0:
			print(f"{timeis()} {red}{pattern} ")
	
	# save csv of most common patterns
	most_common_patterns_df = pd.DataFrame.from_dict(used_infl, orient = "index")
	most_common_patterns_df.sort_values(0, inplace=True, ascending=False)
	most_common_patterns_df.to_csv("output/most common patterns.csv", sep="\t", header=None)


def generate_inflection_patterns_json(inflection_tables_dict):
	"""make a json file of all inflection patterns for use in other apps"""
	print(f"{timeis()} {green}generating inflection patterns html json")
	inflection_tables_html_dict = {}

	for pattern in inflection_tables_dict:
		df_table = inflection_tables_dict[pattern]["df"].copy()
		df_table.fillna("", inplace=True)
		df_rows = df_table.shape[0]
		df_columns = df_table.shape[1]

		for rows in range(0, df_rows):
			for columns in range(0, df_columns, 2): # 1 to 0
				html_cell = df_table.iloc[rows, columns]
				html_cell = re.sub(r"(.+)", f"<b>\\1</b>", html_cell) # add bold
				html_cell = re.sub("\\n", "<br>", html_cell) # add line breaks
				df_table.iloc[rows, columns] = html_cell

		column_list = []
		for i in range(1, df_columns, 2):
			column_list.append(i)

		df_table.drop(df_table.columns[column_list], axis=1, inplace=True)
		html_table = df_table.to_html(escape=False)
		html_table = re.sub("Unnamed.+", "", html_table)
		html_table = re.sub("NaN", "", html_table)
		html_table = re.sub(' style="text-align: right;"', "", html_table)
		html_table = re.sub('border="1" ', '', html_table)
		html_table = re.sub('table class="dataframe"',
							'table class="inflection-table"', html_table)
		html_table = re.sub('<thead>\n', "", html_table)
		html_table = re.sub('</thead>\n', "", html_table)
		html_table = re.sub('<tbody>\n', "", html_table)
		html_table = re.sub('</tbody>\n', "", html_table)
		html_table = re.sub('\n', "", html_table)
		html_table = re.sub('\t', "", html_table)
		html_table = re.sub('      ', "", html_table)
		html_table = re.sub('    ', "", html_table)
		html_table = re.sub('  ', "", html_table)

		inflection_tables_html_dict[pattern] = {"df": "", "like": ""}
		inflection_tables_html_dict[pattern]["df"] = html_table
		inflection_tables_html_dict[pattern]["like"] = inflection_tables_dict[pattern]["like"]

	inflection_tables_html_df = pd.DataFrame(inflection_tables_html_dict)
	inflection_tables_html_df.to_json(
		"output/inflection tables html.json", force_ascii=False, orient="columns", indent=4)
	inflection_tables_html_df.to_json(
		"../dpd-app/data/inflection tables html.json", force_ascii=False, orient="columns", indent=4)


def generate_html_inflection_table(
	make_tables,
	changed_headwords,
	inflection_table_index_dict,
	inflection_tables_dict,
	dpd_df,
	dpd_df_length,
	headwords_list
	):

	print(f"{timeis()} {green}generating html inflection tables")

	indeclinables = ["abbrev", "abs", "ger", "ind", "inf", "prefix"]
	conjugations = ["aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"]
	declensions = ["adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron", "prp", "ptp", "root", "suffix", "ve"]

	for row in range(dpd_df_length): # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \\d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None: #stem contains "!.+" - must get inflection table but no synonsyms
			stem = re.sub("!", "", stem)
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]
		
		if make_tables == True:
			changed_headwords = headwords_list

		if headword in changed_headwords:
			if row % 5000 ==0 :
				print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")

			html_file = open(f"output/html tables/{headword}.html", "w")
				
			if stem == "-":
				html_file.write(f"<p><b>{headword_clean}</b> is indeclinable")

			elif stem == "!":
				html_file.write(f"<p>click on <b>{pattern}</b> for inflection table")

			else:
				df_table = inflection_tables_dict[pattern]["df"].copy()
				df_table.fillna("", inplace=True)
				df_rows = df_table.shape[0]
				df_columns = df_table.shape[1]

				for rows in range(0, df_rows): 
					for columns in range(0, df_columns, 2): #1 to 0
						html_cell = df_table.iloc[rows, columns]
						# html_cell = re.sub(r"(.+)", f"<b>\\1</b>", html_cell) # add bold
						html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell) # add stem
						inflected_words = html_cell.split("\n")
						for inflected_word in inflected_words:
							if inflected_word not in allwords_set:
								# html_cell = re.sub(f"\\b{inflected_word}\\b", f"<span class='gray'>{inflected_word}</span>", html_cell)
								html_cell = re.sub(f"\\b{inflected_word}\\b", f"<span class='gray'>{inflected_word}</span>", html_cell)
								
						html_cell = re.sub(f"(<span class\\='gray'>){stem}(.+?)(<\\/span>)", f"\\1{stem}<b>\\2</b>\\3", html_cell) # add bold to grayed word

						search = re.compile(
							f"(^|\\n){stem}(.+?)(\\n|$)", re.M)
						html_cell = re.sub(
							search, 
							f"\\1{stem}<b>\\2</b>\\3", 
							html_cell) # add bold
						html_cell = re.sub(
							"\\n",
							"<br>",
							html_cell) # add line breaks
						df_table.iloc[rows, columns] = html_cell

				column_list = []
				for i in range(1, df_columns, 2):
					column_list.append(i)

				df_table.drop(df_table.columns[column_list], axis=1, inplace=True)
				html_table = df_table.to_html(escape=False)
				html_table = re.sub("Unnamed.+", "", html_table)
				html_table = re.sub("NaN", "", html_table)
				html_table = re.sub(' style="text-align: right;"', "", html_table)
				html_table = re.sub('border="1" ', '', html_table)

				# write header info

				if inflection_table_index_dict[pattern] != "irreg":
					if pos in declensions:
						heading = (f"""<p class="heading"><b>{headword_clean}</b> is <b>{pattern}</b> declension like <b>{inflection_table_index_dict[pattern]}</b></p>""")
					if pos in conjugations:
						heading = (f"""<p class="heading"><b>{headword_clean}</b> is <b>{pattern}</b> conjugation like <b>{inflection_table_index_dict[pattern]}</b></p>""")

				if inflection_table_index_dict[pattern] == "irreg":
					if pos in declensions:
						heading = (f"""<p class="heading"><b>{headword_clean}</b> is <b>{pattern}</b> irregular declension</p>""")
					if pos in conjugations:
						heading = (f"""<p class="heading"><b>{headword_clean}</b> is <b>{pattern}</b> irregular conjugation</p>""")

				html = heading + html_table 
				html_file.write(html)


def delete_unused_html_tables(
	headwords_list
	):

	file_dir = "output/html tables/"
	file_ext = ".html"
	del_unused_files(headwords_list, file_dir, file_ext)


############# transliteration #############

def export_changed_inflections_to_json (
	all_inflections_dict,
	changed_headwords,
	added_sandhi
	):
	# print(f"{timeis()} {green}exporting changed inflections to json")

	changed_inflections_dict = {}
	for headword in all_inflections_dict:
		if (headword in changed_headwords or
		headword in added_sandhi):
			changed_inflections_dict[headword] = {"inflections": 
			list(all_inflections_dict[headword]["inflections"])}

	changed_inflections_dict_json = json.dumps(
		changed_inflections_dict, ensure_ascii=False, indent=4)

	with open("output/changed inflections.json", "w") as f:
		f.write(changed_inflections_dict_json)


def transliterate_aksharamukha (
	all_inflections_dict,
	changed_headwords, 
	added_sandhi
	):
	# print(f"{timeis()} {green}transliterating inflections to sinhala devanagari thai")

	translit_dict = {}
	for headword in all_inflections_dict:
		if (headword in changed_headwords or 
		headword in added_sandhi or
		all_inflections_dict[headword]["sinhala"] == ""):

			translit_dict[headword] = ""
			for inflection in all_inflections_dict[headword]["inflections"]:
				translit_dict[headword] += f"{inflection} "
	
	translit_df = pd.DataFrame.from_dict(translit_dict, orient="index")
	translit_df = translit_df.dropna()
	translit_df.fillna("", inplace=True)
	translit_df.reset_index(inplace=True)
	concat_df_len = 0
	
	if len(translit_df) != 0:
		print()
		inflections = translit_df[0].to_csv(index=None, quoting=None, header=None)

		sinhala = transliterate.process(
			"IASTPali", "Sinhala", inflections, post_options=['SinhalaPali'])

		devanagari = devanagari = transliterate.process(
			"IASTPali", "Devanagari", inflections)

		thai = transliterate.process(
			"IASTPali", "Thai", inflections)

		sinhala_df = pd.DataFrame(sinhala.split("\n"))
		devanagari_df = pd.DataFrame(devanagari.split("\n"))
		thai_df = pd.DataFrame(thai.split("\n"))

		concat_df = pd.concat([translit_df, sinhala_df, devanagari_df, thai_df], axis=1)
		concat_df = concat_df.dropna()
		concat_df_len = len(concat_df)

		for row in range(len(concat_df)):
			headword = concat_df.iloc[row, 0]
			inflections = concat_df.iloc[row, 1]
			sinhala = concat_df.iloc[row, 2]
			devanagari = concat_df.iloc[row, 3]
			thai = concat_df.iloc[row, 4]

			if len(concat_df) >= 1000:
				if row % 1000 == 0:
					print(f"{timeis()} {white}{row}\t{headword}")

			all_inflections_dict[headword]["sinhala"] = set(sinhala.split())
			all_inflections_dict[headword]["devanagari"] = set(devanagari.split())
			all_inflections_dict[headword]["thai"] = set(thai.split())

	return all_inflections_dict, concat_df_len
	

def transliterate_path_nirvana():
	# pali-script.mjs produces different orthography from akshramusha

	# print(f"{timeis()} {green}running node.js transliteration", end= " ")
	try:
		output = check_output(["node", "transliterate inflections.mjs"])
		print(f"{white}{output}")
	except Exception as e:
		print(f"{red}{e}")


def import_path_nirvana_transliterations (
	all_inflections_dict
	):

	print(f"{timeis()} {green}importing path nirvana inflections", end=" ")
	with open("output/changed inflections translit.json", "r") as f:
		new_inflections = json.load(f)
		print(f"{white}{len(new_inflections)}")

	counter = 0
	sinhala_count = 0
	devanagari_count = 0
	thai_count = 0
	length = len(new_inflections)

	print(f"{timeis()} {green}updating all inflections dict")
	for headword in new_inflections:

		if 5000 % length == 0:
			print(f"{timeis()} {white}{counter}/{length}\t{headword}")

		for sinhala_word in new_inflections[headword]["sinhala"]:
			if sinhala_word not in all_inflections_dict[headword]["sinhala"]:
				all_inflections_dict[headword]["sinhala"].add(sinhala_word)
				sinhala_count += 1

		for devanagari_word in new_inflections[headword]["devanagari"]:
			if devanagari_word not in all_inflections_dict[headword]["devanagari"]:
				all_inflections_dict[headword]["devanagari"].add(devanagari_word)
				devanagari_count += 1

		for thai_word in new_inflections[headword]["thai"]:
			if thai_word not in all_inflections_dict[headword]["thai"]:
				all_inflections_dict[headword]["thai"].add(thai_word)
				thai_count += 1
		counter += 1

	print(f"{timeis()} {green}sinhala: {white}{sinhala_count}")
	print(f"{timeis()} {green}devanagari: {white}{devanagari_count}")
	print(f"{timeis()} {green}thai: {white}{thai_count}")

	return all_inflections_dict


def clean_machine(text):
	text = text.lower()
	text = re.sub("\\d", "", text)
	# sometmes no space afterwards, so needs space
	text = re.sub("\\.", " ", text)
	text = re.sub(",", " ", text)
	text = re.sub(";", " ", text)
	text = re.sub(":", " ", text)
	text = re.sub("‘", "", text)
	text = re.sub("’", "", text)
	text = re.sub("`", "", text)
	text = re.sub("“", "", text)
	text = re.sub("”", "", text)
	text = re.sub('"', "", text)
	text = re.sub("!", "", text)
	text = re.sub("\\?", "", text)
	text = re.sub("\\+", "", text)
	text = re.sub("\\*", "", text)
	text = re.sub("=", "", text)
	text = re.sub("﻿", "", text)
	text = re.sub("§", " ", text)
	text = re.sub("\\(", " ", text)
	text = re.sub("\\)", " ", text)
	text = re.sub("\\[", " ", text)
	text = re.sub("\\]", " ", text)
	text = re.sub("\\{", " ", text)
	text = re.sub("\\}", " ", text)
	text = re.sub("-", " ", text)
	text = re.sub("–", "", text)
	text = re.sub("—", " ", text)
	text = re.sub("_", "", text)
	text = re.sub("–", "", text)
	text = re.sub("…", " ", text)
	text = re.sub("\t", " ", text)
	text = re.sub("\n", " \n ", text)
	text = re.sub("  ", " ", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	text = re.sub("॰", "", text)
	text = re.sub("ï", "i", text)
	text = re.sub("ü", "u", text)
	return text
