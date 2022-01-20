from modules import *

import pandas as pd
import pickle
from aksharamukha import transliterate
import re
import os

create_inflection_table_index()
create_inflection_table_df()
test_inflection_pattern_changed()
create_dpd_df()
test_for_missing_stem_and_pattern()
test_for_wrong_patterns()
test_for_differences_in_stem_and_pattern()
test_if_inflections_exist()
generate_changed_inflected_forms_df()
generate_html_inflection_table()
generate_changed_inflected_forms_df()
transcribe_new_inflections()
combine_old_and_new_translit_dataframes()
export_translit_to_pickle()
