import re
import warnings
import pandas as pd
import pickle
from modules import *

warnings.simplefilter(action='ignore', category=FutureWarning)

def main():
	create_inflection_table_index()
	create_inflection_table_df()
	test_inflection_pattern_changed()
	create_dpd_df()
	test_for_missing_stem_and_pattern()
	test_for_wrong_patterns()
	test_for_differences_in_stem_and_pattern()
	test_if_inflections_exist()
	generate_changed_inflected_forms_df()
	combine_old_and_new_dataframes()
	export_inflections_to_pickle()
	create_all_inflections_df()
	make_list_of_all_inflections_no_meaning()
	make_list_of_all_inflections_no_eg2()
	read_and_clean_sutta_text()
	make_comparison_table()
	html_find_and_replace()

main()