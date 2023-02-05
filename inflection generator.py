#!/usr/bin/env python3.10
# coding: utf-8


from modules import *
from timeis import tic, toc
import argparse
from grammardict import *

if __name__ == "__main__":

    tic()

    # option -ri to regenerate the inflection dicitonary
    # option -rt to regenerate the inflection tables

    parser = argparse.ArgumentParser()
    parser.add_argument("--regeninflect", "-ri", 
        help="regenerate the inflection dictionary", action="store_true")
    parser.add_argument("--regentables", "-rt", 
        help="regenerate the inflection tables", action="store_true")
    args = parser.parse_args()

    (inflection_table_index_df,
    inflection_table_index_length,
    inflection_table_index_dict
    ) = create_inflection_table_index()

    if args.regeninflect:

        generate_inflection_tables_dict(
            inflection_table_index_df, 
            inflection_table_index_length
            )

    (inflection_table_df
    ) = create_inflection_table_df()

    (inflection_tables_dict,
    pattern_changed
    ) = test_inflection_pattern_changed(
        inflection_table_index_df,
        inflection_table_index_length,
        inflection_table_index_dict,
        inflection_table_df
        )

    (dpd_df,
    dpd_df_length,
    headwords_list
    ) = create_dpd_df()

    old_inflections_dict = import_old_inflections_dict()

    test_for_missing_stem_and_pattern(
        dpd_df,
        dpd_df_length
        )

    test_for_wrong_patterns(
        inflection_table_index_df,
        dpd_df,
        dpd_df_length
        )

    changed_headwords = test_for_differences_in_stem_and_pattern(
        pattern_changed,
        dpd_df,
        dpd_df_length,
        old_inflections_dict
        )

    changed_headwords = test_for_missing_html(
        headwords_list,
        changed_headwords
    )

    if args.regeninflect:

        all_inflections_dict = generate_all_inflections_dict(
            inflection_tables_dict,
            dpd_df,
            dpd_df_length
        )

    else:

        all_inflections_dict = update_all_inflections_dict(
            inflection_tables_dict,
            dpd_df,
            dpd_df_length,
            old_inflections_dict,
            changed_headwords
        )

    unused_patterns(
        inflection_table_index_df,
        dpd_df
        )

    if args.regentables:
        make_tables = True

    else:
        make_tables = False

    generate_inflection_patterns_json(
        inflection_tables_dict
    )

    generate_html_inflection_table(
        make_tables,
        changed_headwords,
        inflection_table_index_dict,
        inflection_tables_dict,
        dpd_df,
        dpd_df_length,
        headwords_list
        )

    delete_unused_html_tables(
        headwords_list
    )

    toc()
