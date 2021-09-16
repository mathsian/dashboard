import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

cohort_dropdown = dbc.DropdownMenu(id="academic-cohort-dropdown", label="Cohort")

subject_dropdown = dbc.DropdownMenu(
    id = "subject-dropdown",
    label = "Subject"
)
assessment_dropdown = dbc.DropdownMenu(
    id = "assessment-dropdown",
    label = "Assessment"
)

cardheader_layout = dbc.Row([
    dbc.Col(html.Div("Cohort")),
    dbc.Col(cohort_dropdown),
    dbc.Col(html.Div("Subject")),
    dbc.Col(subject_dropdown),
    dbc.Col(html.Div("Assessment")),
    dbc.Col(assessment_dropdown)
])

sidebar_layout = html.Div("SF academic sidebar")


@app.callback([
    Output("academic-cohort-dropdown", "label"),
    Output("academic-cohort-dropdown", "children"),
    Output("subject-dropdown", "label"),
    Output("subject-dropdown", "children"),
    Output("assessment-dropdown", "label"),
    Output("assessment-dropdown", "children"),
], [
    Input("location", "pathname"),
    Input("location", "search"),
], [
    State("subject-dropdown", "label"),
    State("assessment-dropdown", "label"),
])
def update_assessments(pathname, search, subject, assessment):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', ['2123'])[0]
    print(f"Cohort {cohort}")
    subjects = [s_c for s_c, s_n in data.get_subjects(cohort)]
    subject = search_dict.get("subject", subjects)[0]
    print(f"Subject {subject}")
    assessments = data.get_assessments(cohort, subject)
    assessment = search_dict.get("assessment", assessments)[0].replace('+', ' ')
    assessment_items = []
    for ass in assessments:
        s = urlencode(query={'cohort': cohort, 'subject': subject, 'assessment': ass})
        assessment_items.append(dbc.DropdownMenuItem(ass, href=f'{pathname}?{s}'))
    subject_items = []
    for sub in subjects:
        s = urlencode(query={'cohort': cohort, 'subject': sub})
        subject_items.append(dbc.DropdownMenuItem(sub, href=f'{pathname}?{s}'))
    cohort_items = []
    for c in ['2022', '2123']:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    return (cohort, cohort_items, subject, subject_items, assessment, assessment_items)
