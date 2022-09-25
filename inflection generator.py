#!/usr/bin/env python3.10
# coding: utf-8


from modules import *
from timeis import tic, toc
import argparse
from grammardict import *

if __name__ == "__main__":

	# option -ri to regenerate the inflection dicitonary
	# option -rg to regenerate the grammar dicitonary
	# option -rt to regenerate the inflection tables

	parser = argparse.ArgumentParser()
	parser.add_argument("--regeninflect", "-ri", help="regenerate the inflection dictionary", action="store_true")
	parser.add_argument("--regengram", "-rg", help="regenerate the grammar dictionary", action="store_true")
	parser.add_argument("--regentables", "-rt", help="regenerate the inflection tables", action="store_true")
	args = parser.parse_args()
	
	tic()
	create_inflection_table_index()
	if args.regeninflect:
		generate_inflection_tables_dict()
	create_inflection_table_df()
	test_inflection_pattern_changed()
	create_dpd_df()
	import_old_inflections_dict()
	test_for_missing_stem_and_pattern()
	test_for_wrong_patterns()
	test_for_differences_in_stem_and_pattern()
	changed_headwords = test_for_missing_html()
	if args.regeninflect:
		generate_all_inflections_dict()
	else:
		update_all_inflections_dict()
	unused_patterns()

	if args.regentables:
		make_tables = True
	else:
		make_tables = False
	generate_html_inflection_table(make_tables, changed_headwords)

	transliterate_inflections()
	delete_unused_html_tables()
	toc()

	# generate grammar dict

	tic()
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



