#!/usr/bin/env python3.10
# coding: utf-8

import pandas as pd
import pickle
import subprocess
from timeis import timeis, yellow, green, white, red, line, tic, toc
from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry
from pathlib import Path
import re
from functools import reduce
import json
import argparse

#only if you don't want to install writemdict library
import sys
sys.path.insert(1, '../exporter/writemdict') 

from writemdict import MDictWriter
import re

def setup():

	print(f"{timeis()} {yellow}grammar dictionary")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}importing inflection tables dict")

	with open("output/inflection tables dict", "rb") as p:
		inflection_tables_dict = pickle.load(p)

	print(f"{timeis()} {green}creating dpd dataframe")
	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)
	
	dpd_df_length = dpd_df.shape[0]
	headwords_list = dpd_df["Pāli1"].tolist()
	
	nouns = ['fem', 'masc', 'nt', ]
	verbs = ['aor', 'cond', 'fut', 'imp', 'imperf', 'opt', 'perf', 'pr']
	
	indeclineables = ['abbrev', 'abs', 'ger', 'ind', 'inf', 'prefix']
	others = ['cs', 'adj', 'card', 'letter', 'ordin', 'ordinal', 'pp', 'pron', 'prp', 'ptp', 'root', 'sandhi', 'suffix', 'var', 've']

	dpd_df.loc[dpd_df['POS'].isin(nouns), 'POS'] = 'noun'
	dpd_df.loc[dpd_df['POS'].isin(verbs), 'POS'] = 'verb'
	dpd_df.loc[dpd_df['Grammar'].str.contains('adv'), 'POS'] = 'adv'
	dpd_df.loc[dpd_df['Grammar'].str.contains('excl'), 'POS'] = 'excl'
	dpd_df.loc[dpd_df['Grammar'].str.contains('prep'), 'POS'] = 'prep'
	dpd_df.loc[dpd_df['Grammar'].str.contains('emph'), 'POS'] = 'emph'
	dpd_df.loc[dpd_df['Grammar'].str.contains('interr'), 'POS'] = 'interr'

	dpd_df['Pāli3'] = dpd_df['Pāli1'].str.replace(" \\d*$", "", regex=True)
	dpd_df.sort_values(by=['Pāli3', 'POS'], inplace=True)

	return dpd_df, dpd_df_length, headwords_list, inflection_tables_dict


def generate_tipitaka_word_set():
	print(f"{timeis()} {green}importing all tipitaka words", end=" ")
	tipitaka_words_df = pd.read_csv(
		'../frequency maps/output/word count csvs/tipiṭaka.csv', sep="\t", header=None)
	all_tipitaka_words = set(tipitaka_words_df[0].to_list())
	print(f"{white}{len(all_tipitaka_words)}")
	return all_tipitaka_words


def generate_sandhi_word_set():
	print(f"{timeis()} {green}importing all sandhi words", end=" ")
	sandhi_words_df = pd.read_csv('output/sandhi/matches.csv', sep="\t")

	sandhi_words_df = sandhi_words_df['split'].str.replace(
		" + ", "-", regex=False)
	sandhi_words_df = sandhi_words_df.str.split("-")
	all_sandhi_word_list = sandhi_words_df.to_list()

	all_sandhi_words = set()

	for little_list in all_sandhi_word_list:
		for word in little_list:
			all_sandhi_words.add(word)

	print(f"{white}{len(all_sandhi_words)}")
	return all_sandhi_words


def combine_word_sets():

	all_tipitaka_words = generate_tipitaka_word_set()
	all_sandhi_words = generate_sandhi_word_set()
	print(f"{timeis()} {green}making all words set", end=" ")
	all_words = all_tipitaka_words | all_sandhi_words
	print(f"{white}{len(all_words)}")
	with open("output/allwords set", "wb") as p:
		pickle.dump(all_words, p)

	# to json 
	all_words_json = json.dumps(list(all_words), ensure_ascii=False, indent=4)
	with open("output/allwords set.json", "w") as f:
		f.write(all_words_json)
	with open("../dpd-app/data/allwords set.json", "w") as f:
		f.write(all_words_json)
	return all_words


def generate_grammar_dict(dpd_df, dpd_df_length, inflection_tables_dict, args, changed_headwords):
	print(f"{timeis()} {green}generating grammar dict")

	if args.regengram:
		grammar_dict = {}
	else:
		with open('output/grammardict', 'rb') as p:
			grammar_dict = pickle.load(p)

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \\d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None: #stem contains "!.+" - must get inflection table but no synonsyms
			stem = re.sub("!.+", "!", stem)
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]

		if row % 5000 == 0 and args.regengram:
			print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")
	

		def update_headword():
			if stem == "-":
				if headword in grammar_dict.keys():
					if headword_clean in grammar_dict[headword].keys():
						grammar_dict[headword][headword_clean].append((pos, "indeclineable"))
					else:
						grammar_dict[headword].update({headword_clean: [(pos, "indeclineable")]})
				else:
					grammar_dict.update({headword: {headword_clean: [(pos, "indeclineable")]}})

			elif stem == "!":
				pass

			else:
				df_table = inflection_tables_dict[pattern]["df"].copy()
				df_table.fillna("", inplace=True)
				df_rows = df_table.shape[0]
				df_columns = df_table.shape[1]

				for rows in range(0, df_rows): 
					for columns in range(0, df_columns, 2): #1 to 0
						html_cell = df_table.iloc[rows, columns]
						html_cell = re.sub(r"(.+)", f"{stem}\\1", html_cell) # add stem
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
								if headword in grammar_dict.keys():
									if inflection in grammar_dict[headword].keys():
										grammar_dict[headword][inflection].append((pos, grammar))
									else:
										grammar_dict[headword].update({inflection: [(pos, grammar)]})
								else:
									grammar_dict.update({headword:{inflection: [(pos, grammar)]}})
	
		if args.regengram:
			update_headword()
		else:
			if headword in changed_headwords:
				try:
					del grammar_dict[headword]
				except:
					pass
				print(f"{timeis()} {white}updating\t{headword}")
				update_headword()


	print(f"{timeis()} {green}grammar dict size {white}{len(grammar_dict)}")
	with open('output/grammardict', 'wb') as p:
		pickle.dump(grammar_dict, p)
	return grammar_dict


def build_html_dict(all_words_set):
	"""build a new grammar dict based on aggregatng inflections & html"""

	print(f"{timeis()} {green}building html dict", end=" ")
	
	with open('output/grammardict', 'rb') as p:
		grammar_dict = pickle.load(p)
	
	with open('../exporter/assets/dpd-grammar.css', 'r') as c:
		grammar_css = c.read()

	grammar_dict_html = {}

	exclude = ["prefix", "suffix"]

	for headword, inflections in grammar_dict.items():
		headword_clean = re.sub(" \\d*$", "", headword)
		for inflection, grammars in inflections.items():
			for grammar in grammars:
				pos = grammar[0]
				gram = grammar[1]
				if inflection in all_words_set and pos not in exclude:
					if gram == "indeclineable":
						html_line = f"<tr><td><b>{pos}</b></td><td colspan='3'>{gram}</td></tr>"
					else:
						html_line = f"<tr><td><b>{pos}</b></td><td>{gram}</td><td>of</td><td>{headword_clean}</td></tr>"
					if not inflection in grammar_dict_html.keys():
						grammar_dict_html[inflection] = f"{grammar_css}<body><div class='grammar'><table class='grammar'>{html_line}"
					else:
						if not html_line in grammar_dict_html[inflection]:
							grammar_dict_html[inflection] += html_line

	for item in grammar_dict_html:
		grammar_dict_html[item] += f"</table></div></body>"

	print(f"{white} {len(grammar_dict_html)}")
	return grammar_dict_html


def make_grammar_data_df(grammar_dict_html):
	print(f"{timeis()} {green}generating grammar dict")
	grammar_data_list = []
	grammar_data_list_mdict = []
	for key, value in grammar_dict_html.items():
		synonyms = [key]
		for synoym in synonyms:
			if re.findall("ṃ", synoym):
				synoym1 = re.sub("ṃ", "ṁ", synoym)
				synonyms += [synoym1]
				synoym2 = re.sub("ṃ", "ŋ", synoym)
				synonyms += [synoym2]

		grammar_data_list += [[f"{key}", f"""{value}""", "", synonyms]]
		grammar_data_list_mdict += [[f"{key}", f"""<h3>{key}</h3>{value}""", "", synonyms]]

	grammar_data_df = pd.DataFrame(grammar_data_list)
	grammar_data_df.columns = [
            "word", "definition_html", "definition_plain", "synonyms"]

	grammar_data_df_mdict = pd.DataFrame(grammar_data_list_mdict)
	grammar_data_df_mdict.columns = [
            "word", "definition_html", "definition_plain", "synonyms"]

	return grammar_data_df, grammar_data_df_mdict


def make_goldendict(grammar_data_df):
	print(f"{timeis()} {green}parsing grammar data")
	# global dict_data
	dict_data = grammar_data_df.to_dict(orient="records")

	def item_to_word(x):
		return DictEntry(
				word=x["word"],
				definition_html=x["definition_html"],
				definition_plain=x["definition_plain"],
				synonyms=x["synonyms"],
			)

	words = list(map(item_to_word, dict_data))

	ifo = ifo_from_opts(
            {
                "bookname": "DPD Grammar",
                "author": "Bodhirasa",
                "description": "DPD Grammar",
                "website": "https://digitalpalidictionary.github.io",
            }
        )

	print(f"{timeis()} {green}writing goldendict")
	zip_path = Path("dpd-grammar.zip")
	export_words_as_stardict_zip(words, ifo, zip_path)

	# copy to exporter/share
	source_dir = "dpd-grammar.zip"
	dest_dir = "../exporter/share/dpd-grammar-goldendict.zip"

	try:
		subprocess.run(['mv', '--backup=numbered', source_dir, dest_dir], check=True)
	except Exception as e:
		print(f"{timeis()} {red}{e}")


def synonyms(all_items, item):
    all_items.append((item['word'], item['definition_html']))
    for word in item['synonyms']:
        if word != item['word']:
            all_items.append((word, f"""@@@LINK={item["word"]}"""))
    return all_items


def convert_to_mdict(dpd_data_dict):
	ifo = {
		"bookname": "DPD Grammar",
		"author": "Bodhirasa",
		"description": "DPD Grammar",
		"website": "https://digitalpalidictionary.github.io",
	}
	dpd_data = reduce(synonyms, dpd_data_dict, [])
	writer = MDictWriter(
		dpd_data, title=ifo['bookname'], description=f"<p>by {ifo['author']} </p> <p>For more infortmation, please visit <a href=\"{ifo['website']}\">{ifo['description']}</a></p>")
	outfile = open('../exporter/share/dpd-grammar-mdict.mdx', 'wb')
	writer.write(outfile)
	outfile.close()


def make_mdict(grammar_data_df_mdict):
	print(f"{timeis()} {green}writing mdict")

	dict_data = grammar_data_df_mdict.to_dict(orient="records")
	convert_to_mdict(dict_data)


def make_raw_inflections_table(inflection_tables_dict):
	print(f"{timeis()} {green}generting list of raw inflections")

	output_csv = open("output/raw inflections.csv", "w")
	output_csv.write(f"pattern\tdescription\tpattern name\n")

	for pattern_name, table in inflection_tables_dict.items():

		df_table = inflection_tables_dict[pattern_name]["df"]
		df_table.fillna("", inplace=True)
		df_rows = df_table.shape[0]
		df_columns = df_table.shape[1]

		for rows in range(0, df_rows):
			for columns in range(0, df_columns, 2):  # 1 to 0
				patterns = df_table.iloc[rows, columns]
				patterns = patterns.split("\n")
				description = df_table.iloc[rows, columns+1]
				if description == "":
					description = "in comps"
				for pattern in patterns:
					if pattern != "":
						output_csv.write(f"{pattern}\t{description}\t{pattern_name}\n")

	output_csv.close()
	pattern_df = pd.read_csv("output/raw inflections.csv", sep="\t", dtype=str)
	pattern_df.sort_values(
		["pattern", "description", "pattern name"], inplace=True)
	pattern_df.to_csv("output/raw inflections.csv", sep="\t", index=None)


if __name__ == "__main__":

	tic()
	parser = argparse.ArgumentParser()
	parser.add_argument("--regengram", "-r", help="regenerate the grammar dictionary", action="store_true")
	args = parser.parse_args()

	changed_headwords = ["akata 1", "akakkasa"]

	dpd_df, dpd_df_length, headwords_list, inflection_tables_dict = setup()
	all_words_set = combine_word_sets()
	generate_grammar_dict(
		dpd_df, dpd_df_length, inflection_tables_dict, args, changed_headwords)
	grammar_dict_html = build_html_dict(all_words_set)

	grammar_data_df, grammar_data_df_mdict = make_grammar_data_df(
		grammar_dict_html)
	make_goldendict(grammar_data_df)
	make_mdict(grammar_data_df_mdict)
	make_raw_inflections_table(inflection_tables_dict)
	toc()
