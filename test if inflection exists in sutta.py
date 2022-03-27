import warnings
from modules import *
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

def inflection_exists_in_sutta():
	# convert_dpd_ods_to_csv()
	create_inflection_table_index()
	create_inflection_table_df()
	test_inflection_pattern_changed()
	create_dpd_df()
	test_for_missing_stem_and_pattern()
	test_for_wrong_patterns()
	test_for_differences_in_stem_and_pattern()
	test_if_inflections_exist_suttas()
	generate_changed_inflected_forms()
	combine_old_and_new_dataframes()
	export_inflections_to_pickle()
	make_list_of_all_inflections()
	make_list_of_all_inflections_no_meaning()
	make_list_of_all_inflections_no_eg1()
	make_list_of_all_inflections_no_eg2()
	read_and_clean_sutta_text()
	make_comparison_table()
	html_find_and_replace()
	write_html()


inflection_exists_in_sutta()
