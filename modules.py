import pandas as pd
import re
import pickle
from pandas_ods_reader import read_ods
import os
from aksharamukha import transliterate


def create_inflection_table_index():

	global inflection_table_index_df
	inflection_table_index_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="index", dtype=str)

	inflection_table_index_df.fillna("", inplace=True)

	global inflection_table_index_length
	inflection_table_index_length = len(inflection_table_index_df)

	global inflection_table_index_dict
	inflection_table_index_dict = dict(zip(inflection_table_index_df.iloc[:, 0], inflection_table_index_df.iloc[:, 2]))


def create_inflection_table_df():
	print("~" * 40)
	print("creating inflection_table_df")

	global inflection_table_df
	inflection_table_df = pd.read_excel("declensions & conjugations.xlsx", sheet_name="declensions", dtype=str)

	inflection_table_df = inflection_table_df.shift(periods=2)

	inflection_table_df.columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK", "BL", "BM", "BN", "BO", "BP", "BQ", "BR", "BS", "BT", "BU", "BV", "BW", "BX", "BY", "BZ", "CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK", "CL", "CM", "CN", "CO", "CP", "CQ", "CR", "CS", "CT", "CU", "CV", "CW", "CX", "CY", "CZ", "DA", "DB", "DC", "DD", "DE", "DF", "DG", "DH", "DI", "DJ", "DK"]

	inflection_table_df.fillna("", inplace=True)


def test_inflection_pattern_changed():
	print("~" * 40)
	print("test if inflection pattern have changed:")

	global pattern_changed
	pattern_changed = []

	for row in range(inflection_table_index_length):
		inflection_name = inflection_table_index_df.iloc[row,0]
		cell_range = inflection_table_index_df.iloc[row,1]
		like = inflection_table_index_df.iloc[row,2]
		irreg = inflection_table_index_df.iloc[row,3]

		col_range_1 = re.sub("(.+?)\d*\:.+", "\\1", cell_range)
		col_range_2 = re.sub(".+\:(.[A-Z]*)\d*", "\\1", cell_range)
		row_range_1 = int(re.sub(".+?(\d{1,3}):.+", "\\1", cell_range))
		row_range_2 = int(re.sub(".+:.+?(\d{1,3})", "\\1", cell_range))

		inflection_table_df_filtered = inflection_table_df.loc[row_range_1:row_range_2, col_range_1:col_range_2]
		inflection_table_df_filtered.Name =  f"{inflection_name}"

		inflection_table_df_filtered.reset_index(drop=True, inplace=True)

		inflection_table_df_filtered.iloc[0,0] = ""

		# replace header

		new_header = inflection_table_df_filtered.iloc[0] #grab the first row for the header
		inflection_table_df_filtered = inflection_table_df_filtered[1:] #take the data less the header row
		inflection_table_df_filtered.columns = new_header #set the header row as the df header

		# replace index

		inflection_table_df_filtered.index = inflection_table_df_filtered.iloc[0:,0]
		inflection_table_df_filtered = inflection_table_df_filtered.iloc[:, 1:]

		# remove unnamed column headers

		inflection_table_df_filtered = inflection_table_df_filtered.rename(columns=lambda x: re.sub('Unnamed.*','',x))

		# test

		try:
			old = pd.read_csv(f"output/patterns/{inflection_name}.csv", sep="\t", index_col=0, na_filter=False) #, header=0
			old.fillna("", inplace=True)
			old = old.rename(columns=lambda x: re.sub('Unnamed.*','',x))
		except:
			print(f"{inflection_name} - doesn't exist - added")
			pattern_changed.append(inflection_name)
			inflection_table_df_filtered.to_csv(f"output/patterns/{inflection_name}.csv", sep="\t")

		if inflection_table_df_filtered.equals(old):
			continue
		elif inflection_name in pattern_changed:
			continue
		elif not inflection_table_df_filtered.equals(old):
			print(f"{inflection_name} - different - updated")
			inflection_table_df_filtered.to_csv(f"output/patterns/{inflection_name}.csv", sep="\t")
			pattern_changed.append(inflection_name)

	if pattern_changed == []:
		print("all patterns identical")
	if pattern_changed != []:
		print("~" * 40)
		print(f"the following patterns have changes and will be generated\n{pattern_changed}")


def create_dpd_df():
	print("~" * 40)
	print("create dpd_df")
	
	global dpd_df
	
	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)

	global dpd_df_length

	dpd_df_length = dpd_df.shape[0]


def test_for_missing_stem_and_pattern():
	print("~" * 40)
	print(f"test for missing stems and patterns:")

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
		print (f"words with missing stems: {missing_stem_string}")
	if missing_pattern_string != "":
		print (f"words with missing patterns: {missing_pattern_string}")
	if error == True:
		input("there are stem & pattern errors, please fix them before continuiing")
	else:
		print("no stem & pattern errors found")


def test_for_wrong_patterns():

	print("~" * 40)
	print("testing for wrong patterns:")

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
		print(f"wrong patterns: {wrong_patten_string}")
	if error == True:
		input("wrong patterns - fix 'em!")
	if error == False:
		print("no wrong patterns found")


def test_for_differences_in_stem_and_pattern():
	print("~" * 40)
	print("testing for changes in stem and pattern:")

	global changed
	changed = []
	added_string = ""
	changed_string = ""

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		stem = dpd_df.loc[row, "Stem"]
		pattern = dpd_df.loc[row, "Pattern"]
		new = f"{headword} {stem} {pattern}"

		try:
			pickle_file = open(f"output/pickle test/{headword}","rb")
			old = pickle.load(pickle_file)
			pickle_file.close()
		except:
			added_string += headword + "|"
			changed.append(headword)
			pickle_file = open(f"output/pickle test/{headword}","wb")
			pickle.dump(new,pickle_file)
			pickle_file.close()
			continue

		if old == new:
			continue
		elif old in changed:
			continue
		elif old != new:
			changed_string += headword + "|"
			changed.append(headword)
			pickle_file = open(f"output/pickle test/{headword}","wb")
			pickle.dump(new,pickle_file)
			pickle_file.close()

	if added_string != "":
		print(f"headword / stem / pattern doesnt exist and will be added:")
		print("~" * 40)
		print(added_string)
	if changed_string != "":
		print(f"headword / stem / pattern has changed and will be updated")
		print("~" * 40)
		print(changed_string)
	if changed == []:
		print("no headwords stems or patterns changed")


def test_if_inflections_exist_suttas():

	global inflections_not_exist
	inflections_not_exist = []
	inflections_not_exists_string = ""

	print("~"*40)
	print("test if inflections exists")

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		
		try:
			with open(f"output/inflections/{headword}", "rb") as syn_file:
				pass
			with open(f"output/inflections/{headword}", "rb") as syn_file:
				pass
		
		except:
			inflections_not_exists_string += headword + "|"
			inflections_not_exist.append(headword)

	if inflections_not_exists_string != "":
		print("~"*40)
		print(f"inflection file doesn't exist for:\n{inflections_not_exists_string}")
		print("~"*40)

	if inflections_not_exist == []:
		print("no missing inflection files")


def test_if_inflections_exist_dpd():

	global inflections_not_exist
	inflections_not_exist = []
	inflections_not_exists_string = ""

	print("~"*40)
	print("test if inflections exists")

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		
		try:
			with open(f"output/inflections translit/{headword}", "rb") as syn_file:
				pass
		
		except:
			inflections_not_exists_string += headword + "|"
			inflections_not_exist.append(headword)

	if inflections_not_exists_string != "":
		print("~"*40)
		print(f"inflection file doesn't exist for:\n{inflections_not_exists_string}")
	if inflections_not_exist == []:
		print("no missing inflection files")


def generate_changed_inflected_forms():

	print("~" * 40)
	print("generating changed inflected forms:")

	global new_inflections_dict
	new_inflections_dict = {}

	for row in range(dpd_df_length): #dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None: #stem contains "!.+" - must get inflection table but no synonsyms
			stem = "!"
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]
		metadata = dpd_df.loc[row, "Metadata"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]
		variant = dpd_df.loc[row, "Variant – same constr or diff reading"]

		inflections_string= ""

		if headword in changed or pattern in pattern_changed or headword in inflections_not_exist:
			
			if stem == "-":
				inflections_string += headword_clean + " "

			elif stem == "!":
				inflections_string += headword_clean + " "

			else:
				inflections_string+= headword_clean + " "

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
							replace_string = " "
							matches = re.sub(search_string, replace_string, line)
							inflections_string += matches + " "

				except:
					with open("inflection generator errorlog.txt", "a") as error_log:
						error_log.write(f"error on: {headword}\n")
						print(f"error on: {headword}\n")

			this_word_inflections = {headword : inflections_string}
			new_inflections_dict.update(this_word_inflections)

	if new_inflections_dict != {}:
		new_inflections_df = pd.DataFrame.from_dict(new_inflections_dict, orient='index')
		new_inflections_df.to_csv("output/new inflections.csv", sep="\t", header=False)

	else:
		print("no new inflections")


def generate_html_inflection_table():
	print("~" * 40)
	print("generating html inflection tables")
	print("~" * 40)

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
		metadata = dpd_df.loc[row, "Metadata"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]

		if headword in changed or pattern in pattern_changed or headword in inflections_not_exist:
			print(f"{row}\t{headword}")

			with open(f"output/html tables/{headword}.html", "w") as html_table:
				
				if stem == "-":
					html_table.write(f"<p><b>{headword_clean}</b> is indeclinable")

				elif stem == "!":
					html_table.write(f"<p>click on <b>{pattern}</b> for inflection table")

				else:
					df = pd.read_csv(f"output/patterns/{pattern}.csv", sep="\t", index_col=0)
					df.fillna("", inplace=True, axis=0)
				
					df_rows = df.shape[0]
					df_columns = df.shape[1]

					for rows in range(0, df_rows): 
						for columns in range(0, df_columns, 2): #1 to 0
						
							html_cell = df.iloc[rows, columns]
							syn_cell = df.iloc[rows, columns]	

							if html_cell == "sg" or html_cell == "pl":
								pass

							else:
								html_cell = re.sub(r"(.+)", f"<b>\\1</b>", html_cell) # add bold
								html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell) # add stem
								html_cell = re.sub(r"\n", "<br>", html_cell) # add line breaks
								df.iloc[rows, columns] = html_cell
							
								syn_cell = re.sub(r"(.+)", f"{stem}\\1", syn_cell)
								search_string = re.compile("\n", re.M)
								replace_string = " "
								matches = re.sub(search_string, replace_string, syn_cell)
				
					column_list = []
					for i in range(1, df_columns, 2):
						column_list.append(i)

					df.drop(df.columns[column_list], axis=1, inplace=True)
					table = df.to_html(escape=False)
					table = re.sub("Unnamed.+", "", table)
					table = re.sub("NaN", "", table)

					# write header info

					if inflection_table_index_dict[pattern] != "":
						if pos in declensions:
							heading = (f"""<p><b>{headword_clean}</b> is <b>{pattern}</b> declension like <b>{inflection_table_index_dict[pattern]}</b></p>""")
						if pos in conjugations:
							heading = (f"""<p><b>{headword_clean}</b> is <b>{pattern}</b> conjugation like <b>{inflection_table_index_dict[pattern]}</b></p>""")

					if inflection_table_index_dict[pattern] == "":
						if pos in declensions:
							heading = (f"""<p><b>{headword_clean}</b> is <b>{pattern}</b> irregular declension</p>""")
						if pos in conjugations:
							heading = (f"""<p><b>{headword_clean}</b> is <b>{pattern}</b> irregular conjugation</p>""")
				
					html = heading + table 
					html_table.write(html)


def transcribe_new_inflections():
	if new_inflections_dict != {}:
		print("~" * 40)

		new_inflections = open("output/new inflections.csv", "r")
		new_inflections_read = new_inflections.read()
		new_inflections.close()

		new_inflections_translit = open("output/new inflections translit.csv", "w")

		print("converting inflections to sinhala")
		sinhala = transliterate.process("IAST","Sinhala", new_inflections_read, post_options =['SinhalaPali', 'SinhalaConjuncts'])

		print("converting inflections to devanagari")
		devanagari = transliterate.process("IAST","Devanagari",new_inflections_read, post_options = ['DevanagariAnusvara'])

		roman = new_inflections_read.split("\n")[:-1]
		sinhala = sinhala.split("\n")
		devanagari = devanagari.split("\n")

		for i in zip(roman, sinhala, devanagari):	
			new_inflections_translit.write(i[0]+i[1].split("\t")[1]+i[2].split("\t")[1]+"\n")

		new_inflections_translit.close()
	
	else:
		print("no new inflections to transcribe")


def combine_old_and_new_translit_dataframes():
	print("~" * 40)
	print("combing old and new dataframes:")

	global diff
	diff = pd.DataFrame()

	if new_inflections_dict != {}:
		all_inflections_translit = pd.read_csv("output/all inflections translit.csv", header=None, sep="\t")

		new_inflections_translit = pd.read_csv("output/new inflections translit.csv", header=None, sep="\t")

		diff = pd.merge(all_inflections_translit, new_inflections_translit, on=[0], how='outer', indicator='exists')
		# diff.to_csv("output/diff translit.csv", sep="\t", index=None)

		# copy changes

		test1 = diff["exists"] == "both"
		test2 = diff["1_y"] != ""
		filter = test1 & test2
		diff.loc[filter, "1_x"] = diff.loc[filter, "1_y"]

		# add new

		test1 = diff["exists"] == "right_only"
		test2 = diff["1_y"] != ""
		filter = test1 & test2
		diff.loc[filter, "1_x"] = diff.loc[filter, "1_y"]

		# !!! how to delete non existent

		# drop columns and write to csv

		diff.drop(columns=["1_y", "exists"], inplace=True)

		diff.to_csv("output/all inflections translit.csv", sep="\t", index=None, header=False)

		print("all inflections translit.csv updated")

	else:
		print("all inflections translit.csv unchanged")


def export_translit_to_pickle():
	print("~" * 40)
	print("exporting inflections translit to pickle")

	all_inflections = diff

	length = len(all_inflections)

	for row in range(length):

		headword = all_inflections.iloc[row, 0]
		inflections = all_inflections.iloc[row, 1]

		# !!! how to delete headword when no longer exists	??? 
		
		if headword in new_inflections_dict.keys():
			print(headword)

			inflections_list = inflections.split()

			# add ṁ version

			for word in inflections_list:
				if 'ṃ' in word:
					wordṁ = re.sub("ṃ", "ṁ", word) 
					inflections_list.append(wordṁ)

			inflections_list = list(dict.fromkeys(inflections_list))

			with open(f"output/inflections translit/{headword}", "wb") as text_file:
				pickle.dump(inflections_list, text_file)


def combine_old_and_new_dataframes():
	print("~" * 40)
	print("combinging old and new dataframes:")

	global diff
	diff = pd.DataFrame()

	if new_inflections_dict != {}:
		all_inflections_df = pd.read_csv("output/all inflections.csv", header=None, sep="\t")

		new_inflections_df = pd.read_csv("output/new inflections.csv", header=None, sep="\t")

		diff = pd.merge(all_inflections_df, new_inflections_df, on=[0], how='outer', indicator='exists')
		# diff.to_csv("output/diff.csv", sep="\t", index=None, header=False)

		# copy changes

		test1 = diff["exists"] == "both"
		test2 = diff["1_y"] != ""
		filter = test1 & test2
		diff.loc[filter, "1_x"] = diff.loc[filter, "1_y"]

		# add new

		test1 = diff["exists"] == "right_only"
		test2 = diff["1_y"] != ""
		filter = test1 & test2
		diff.loc[filter, "1_x"] = diff.loc[filter, "1_y"]

		# !!! how to delete non existent

		# drop columns and write to csv

		diff.drop(columns=["1_y", "exists"], inplace=True)

		diff.to_csv("output/all inflections.csv", sep="\t", index=None, header=False)

		print("all inflections.csv updated")

	else:
		print("all inflections.csv unchanged")


def export_inflections_to_pickle():

	print("~" * 40)
	print("exporting inflections to pickle")

	all_inflections = diff

	length = len(all_inflections)

	for row in range(length):

		headword = all_inflections.iloc[row, 0]
		inflections = all_inflections.iloc[row, 1]

		# !!! how to delete headword when no longer exists	??? 
		
		if headword in new_inflections_dict.keys():
			print(headword)

			inflections_list = inflections.split()

			# add ṁ version

			inflections_list = list(dict.fromkeys(inflections_list))

			with open(f"output/inflections/{headword}", "wb") as text_file:
				pickle.dump(inflections_list, text_file)


def make_list_of_all_inflections():
	print("~" * 40)
	print("creating all inflections df")

	global all_inflections_df
	all_inflections_df = pd.read_csv("output/all inflections.csv", header=None, sep="\t")

	print("~" * 40)
	print("making master list of all inflections")
	print("~" * 40)

	# global all_inflections_list
	all_inflections_string = ""
	for row in range (all_inflections_df.shape[0]):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]
		all_inflections_string += inflections
		
		if row %5000 == 0:
			print(f"{row} {headword}")

	all_inflections_list = all_inflections_string.split()
	all_inflections_list = list(dict.fromkeys(all_inflections_list))

	global all_inflections_set
	all_inflections_set = set(dict.fromkeys(all_inflections_list))


def make_list_of_all_inflections_no_meaning():

	print("~" * 40)
	print("making list of all inflections with no meaning")
	print("~" * 40)

	global no_meaning_list

	test1 = dpd_df["Meaning IN CONTEXT"] != ""
	test2 = dpd_df["POS"] != "prefix"
	test3 = dpd_df["POS"] != "suffix"
	test4 = dpd_df["POS"] != "cs"
	test5 = dpd_df["POS"] != "ve"
	test6 = dpd_df["POS"] != "idiom"
	test7 = dpd_df["Metadata"] != "yes"
	filter = test1 & test2 & test3 & test4 & test5 & test6 & test7

	no_meaning_df = dpd_df[filter]

	no_meaning_headword_list = no_meaning_df["Pāli1"].tolist()

	no_meaning_df = all_inflections_df[all_inflections_df[0].isin(no_meaning_headword_list)]

	no_meaning_string = ""
	for row in range (all_inflections_df.shape[0]):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]

		if row %5000 == 0:
			print(f"{row} {headword}")

		if headword in no_meaning_headword_list:
			no_meaning_string += inflections

	no_meaning_list = no_meaning_string.split()
	no_meaning_list = list(dict.fromkeys(no_meaning_list))


def make_list_of_all_inflections_no_eg1():

	print("~" * 40)
	print("making list of all inflections with no eg1")
	print("~" * 40)

	global no_eg1_list

	test = dpd_df["Sutta1"] == ""
	no_eg1_df = dpd_df[test]

	no_eg1_headword_list = no_eg1_df["Pāli1"].tolist()

	no_eg1_df = all_inflections_df[all_inflections_df[0].isin(no_eg1_headword_list)]

	no_eg1_string = ""
	for row in range (all_inflections_df.shape[0]):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]

		if row %5000 == 0:
			print(f"{row} {headword}")

		if headword in no_eg1_headword_list:
			no_eg1_string += inflections

	no_eg1_list = no_eg1_string.split()
	no_eg1_list = list(dict.fromkeys(no_eg1_list))


def make_list_of_all_inflections_no_eg2():

	print("~" * 40)
	print("making list of all inflections with no eg2")
	print("~" * 40)

	global no_eg2_list

	test = dpd_df["Sutta2"] == ""
	no_eg2_df = dpd_df[test]

	no_eg2_headword_list = no_eg2_df["Pāli1"].tolist()

	no_eg2_df = all_inflections_df[all_inflections_df[0].isin(no_eg2_headword_list)]

	no_eg2_string = ""
	for row in range (all_inflections_df.shape[0]):
		headword = all_inflections_df.iloc[row, 0]
		inflections = all_inflections_df.iloc[row, 1]

		if row %5000 == 0:
			print(f"{row} {headword}")

		if headword in no_eg2_headword_list:
			no_eg2_string += inflections

	no_eg2_list = no_eg2_string.split()
	no_eg2_list = list(dict.fromkeys(no_eg2_list))

def clean_machine(text):
	text = text.lower()
	text = re.sub("\d", "", text)
	text = re.sub("\.", "", text)
	text = re.sub(",", "", text)
	text = re.sub("‘", "", text)
	text = re.sub(";", "", text)
	text = re.sub("’", "", text)
	text = re.sub("!", "", text)
	text = re.sub("\?", "", text)
	text = re.sub("\+", "", text)
	text = re.sub("﻿", "", text)
	text = re.sub("§", " ", text)
	text = re.sub("\(", "", text)
	text = re.sub("\)", "", text)
	text = re.sub("-", "", text)
	text = re.sub("–", "", text)	
	text = re.sub("\t", " ", text)
	text = re.sub("…", " ", text)
	text = re.sub("–", "", text)
	text = re.sub("\n", " <br> ", text)
	text = re.sub("  ", " ", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	text = re.sub("^ ", "", text)
	return text

def read_and_clean_sutta_text():

	print("~" * 40)
	print("reading and cleaning sutta file")
	print("~" * 40)
	
	global input_path
	input_path = "../pure-machine-readable-corpus/cscd/"

	global output_path
	output_path = "output/html suttas/"

	global sutta_file
	sutta_file = input("paste sutta file name here: ")

	global commentary_file
	commentary_file = input("paste commnetary file name here: ")

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

	print("~" * 40)
	print("making sutta comparison table")

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

	print("~" * 40)
	print("making commentary comparison table")

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

	print("~" * 40)
	print("finding and replacing sutta html")
	print("~" * 40)

	global sutta_text
	global commentary_text

	with open(f"{output_path}{sutta_file}", 'r') as input_file:
		sutta_text = input_file.read()
	
	max_row = sutta_words_df.shape[0]
	row=0

	for word in range(row, max_row):
		pali_word = str(sutta_words_df.iloc[row, 0])
		inflection_exists = str(sutta_words_df.iloc[row, 1])
		meaning_exists = str(sutta_words_df.iloc[row, 2])
		eg1_exists = str(sutta_words_df.iloc[row, 3])
		eg2_exists = str(sutta_words_df.iloc[row, 4])

		if row % 250 == 0:
			print(f"{row}/{max_row}\t{pali_word}")

		row +=1

		if meaning_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "highlight">\\2</span>\\3""", sutta_text)

		elif eg1_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "orange">\\2</span>\\3""", sutta_text)

		elif eg2_exists == "False":

			sutta_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "red">\\2</span>\\3""", sutta_text)

	print("~" * 40)
	print("finding and replacing commentary html")
	print("~" * 40)

	with open(f"{output_path}{commentary_file}", 'r') as input_file:
		commentary_text = input_file.read()
	
	max_row = commentary_words_df.shape[0]
	row=0

	for word in range(row, max_row):
		pali_word = str(commentary_words_df.iloc[row, 0])
		inflection_exists = str(commentary_words_df.iloc[row, 1])
		meaning_exists = str(commentary_words_df.iloc[row, 2])

		if row % 250 == 0:
			print(f"{row}/{max_row}\t{pali_word}")

		row +=1

		if inflection_exists == "False":

			commentary_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "highlight">\\2</span>\\3""", commentary_text)

		elif meaning_exists == "False":

			commentary_text = re.sub(fr"(^|\s)({pali_word})(\s|\n|$)", f"""\\1<span class = "orange">\\2</span>\\3""", commentary_text)


def write_html():
	
	html1 = """
<!DOCTYPE html>
<html>
<head>
<style>
#content, html, body { 
	height: 98%;
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
	color: #9b794b;
	background-color: #221a0e;
	font-size: 15px;}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
	}

::-webkit-scrollbar-button {
    width: 0px;
    height: 0px;
	}

::-webkit-scrollbar-thumb {
    background: #5d6726;
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
    background: #433730;
	}

::-webkit-scrollbar-track {
    background: transparent;
    border: 0px none transparent;
    border-radius: 0px;
	}

::-webkit-scrollbar-corner {
    background: transparent;
	border-radius: 10px;
	}

.highlight {
	color:#7e2801;
    background-color: #feffaa ;
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

	html_file = open(f"{output_path}{sutta_file}.html", "w")
	html_file = open(f"{output_path}{sutta_file}.html", "a")
	html_file.write(html1)
	html_file.write(sutta_text)
	html_file.write(html2)
	html_file.write(commentary_text)
	html_file.write(html3)
	html_file.close
