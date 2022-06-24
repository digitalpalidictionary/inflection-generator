#!/usr/bin/env python3.10
# coding: utf-8

import pandas as pd
import pickle
from timeis import timeis, yellow, green, line, tic, toc
from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry
from pathlib import Path
import re
from functools import reduce

#only if you don't want to install writemdict library
import sys
sys.path.insert(1, '../exporter/writemdict') 

from writemdict import MDictWriter
import re

tic()
print(f"{timeis()} {yellow}grammar dictionary")
print(f"{timeis()} {line}")
print(f"{timeis()} {green}importing inflection tables dict")

with open("output/inflection tables dict", "rb") as p:
	inflection_tables_dict = pickle.load(p)

def create_dpd_df():
	print(f"{timeis()} {green}creating dpd dataframe")

	global dpd_df

	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)

	dpd_df_length = dpd_df.shape[0]
	headwords_list = dpd_df["Pāli1"].tolist()
	return dpd_df, dpd_df_length, headwords_list


def generate_grammar_dict():
	print(f"{timeis()} {green}generating inflection tables")

	# grammar_file = open ("output/grammar dict/grammar dict.csv", "w")
	grammar_dict = {}

	for row in range(dpd_df_length):  # dpd_df_length
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		stem = dpd_df.loc[row, "Stem"]
		if re.match("!.+", stem) != None: #stem contains "!.+" - must get inflection table but no synonsyms
			stem = re.sub("!.+", "!", stem)
		if stem == "*":
			stem = ""
		pattern = dpd_df.loc[row, "Pattern"]
		pos = dpd_df.loc[row, "POS"]
		meaning = dpd_df.loc[row, "Meaning IN CONTEXT"]

		if row %5000 == 0:
			print(f"{timeis()} {row}/{dpd_df_length}\t{headword}")
			
		if stem == "-":
			if inflection not in grammar_dict.keys():
				grammar_dict[inflection] = f"<b>{inflection}</b> is <b>indeclineable</b>"
			elif inflection in grammar_dict.keys():
				grammar_dict[inflection] += f"<br><b>{inflection}</b> is <b>indeclineable</b>"
		
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
							if inflection not in grammar_dict.keys():
								grammar_dict[inflection] = f"<b>{inflection}</b> is <b>{grammar}</b> of <b>{headword}</b>"
							elif inflection in grammar_dict.keys():
								grammar_dict[inflection] += f"<br><b>{inflection}</b> is <b>{grammar}</b> of <b>{headword}</b>"

	return grammar_dict


def make_grammar_data_df():
	print(f"{timeis()} {green}generating grammar dict")
	grammar_data_list = []
	for key, value in grammar_dict.items():
		grammar_data_list += [[f"{key}", f"""{value}""", "", ""]]
	
	grammar_data_df = pd.DataFrame(grammar_data_list)
	grammar_data_df.columns = [
            "word", "definition_html", "definition_plain", "synonyms"]
	return grammar_data_df


def make_goldendict():
	print(f"{timeis()} {green}parsing grammar data")
	global dict_data
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
	zip_path = Path("../exporter/share/grammar.zip")
	export_words_as_stardict_zip(words, ifo, zip_path)
	

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
	writer = MDictWriter(dpd_data, title=ifo['bookname'], description = f"<p>by {ifo['author']} </p> <p>For more infortmation, please visit <a href=\"{ifo['website']}\">{ifo['description']}</a></p>")
	outfile = open('../exporter/share/grammar.mdx', 'wb')
	writer.write(outfile)
	outfile.close()

def make_mdict():
    print(f"{timeis()} {green}writing mdict")    
    convert_to_mdict(dict_data)

dpd_df, dpd_df_length, headwords_list = create_dpd_df()
grammar_dict = generate_grammar_dict()
grammar_data_df = make_grammar_data_df()
make_goldendict()
make_mdict()
toc()
