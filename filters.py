from urllib.parse import parse_qs, urlparse, urlencode
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

from app import app
import data




#
#@app.callback(
#        Output({
#            "type": "filter-dropdown",
#            "filter": "subject"
#        }, "options"),
#    [Input({
#        "type": "filter-dropdown",
#        "filter": "cohort"
#    }, "value")],
#)
#def update_subject_filter(cohort_value):
#    subjects = data.get_subjects(cohort_value)
#    return [{
#            "label": subject_name,
#            "value": subject_code
#        } for subject_code, subject_name in subjects]
#
#
#@app.callback(
#    Output({
#        "type": "dropdown",
#        "page": "academic",
#        "name": "assessment"
#    }, "options"),
#    [Input({
#    "type": "filter-dropdown",
#    "filter": ALL
#}, "value")])
#def update_assessment_dropdown(filter_value):
#    cohort, subject_code = filter_value
#    if not (cohort and subject_code):
#        return []
#    assessment_docs = data.get_data("assessment", "subject_cohort",
#                      (subject_code, cohort))
#    assessment_df = pd.DataFrame.from_records(assessment_docs)
#    if assessment_df.empty:
#        return []
#    assessment_list = assessment_df.sort_values(
#        by="date", ascending=False)["assessment"].unique().tolist()
#    options = [{"label": a, "value": a} for a in assessment_list]
#    return options
#
