############# unused	#############

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

