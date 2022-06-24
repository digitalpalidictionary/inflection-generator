#!/usr/bin/env python3
# coding: utf-8 

from modules import *
from timeis import tic, toc

def inflection_generator_for_dpd():
	tic()
	create_inflection_table_index()
	# generate_inflection_tables_dict()
	create_inflection_table_df()
	test_inflection_pattern_changed()
	create_dpd_df()
	import_old_inflections_dict()
	test_for_missing_stem_and_pattern()
	test_for_wrong_patterns()
	test_for_differences_in_stem_and_pattern()
	# generate_all_inflections_dict()
	update_all_inflections_dict()
	generate_html_inflection_table()
	transliterate_inflections()
	delete_unused_html_tables()
	toc()

inflection_generator_for_dpd()
