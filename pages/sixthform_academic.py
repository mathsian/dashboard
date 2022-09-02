import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
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

cohort_dropdown = dbc.DropdownMenu(id="academic-cohort-dropdown", nav=True)

subject_dropdown = dbc.DropdownMenu(id="subject-dropdown", nav=True)

page_nav = dbc.Nav([
    dbc.NavItem(cohort_dropdown),
    dbc.NavItem(subject_dropdown),
],
                   fill=True)

assessment_nav = dbc.Nav(
    id={
        "type": "nav",
        "section": "sixthform",
        "page": "academic",
        "name": "assessments"
    },
    pills=True,
    vertical=True,
)
layout = [
    dcc.Store("sixthform-academic-store", storage_type='memory'),
    dbc.Row(dbc.Col(page_nav)),
    dbc.Row(dbc.Col(assessment_nav))
]


@app.callback([
    Output("academic-cohort-dropdown", "label"),
    Output("academic-cohort-dropdown", "children"),
    Output("subject-dropdown", "label"),
    Output("subject-dropdown", "children"),
    Output(
        {
            "type": "nav",
            "section": "sixthform",
            "page": "academic",
            "name": "assessments"
        }, "children"),
    Output("sixthform-academic-store", "data")
], [
    Input("location", "pathname"),
    Input("location", "search"),
], [
    State("subject-dropdown", "label"),
])
def update_assessments(pathname, search, subject):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', [curriculum.cohorts[-1]])[0]
    cohort_items = []
    for c in curriculum.cohorts:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    subjects = [s_c for s_c, s_n in data.get_subjects(cohort)]
    if not subjects:
        return cohort, cohort_items, "", [], [], []
    subject = search_dict.get("subject", subjects)[0]
    assessments = data.get_assessments(cohort, subject)
    assessment = search_dict.get("assessment",
                                 assessments)[0].replace('+', ' ')
    assessment_items = []
    for ass in assessments:
        s = urlencode(query={
            'cohort': cohort,
            'subject': subject,
            'assessment': ass
        })
        active = 'exact' if ass == assessment else False
        assessment_items.append(
            dbc.NavItem(
                dbc.NavLink(ass, href=f'{pathname}?{s}',
                            active=bool(active)), ))
    subject_items = []
    for sub in subjects:
        s = urlencode(query={'cohort': cohort, 'subject': sub})
        subject_items.append(dbc.DropdownMenuItem(sub, href=f'{pathname}?{s}'))
    assessment_docs = data.get_data("assessment", "assessment_subject_cohort",
                                    [(assessment, subject, cohort)])
    enrolment_docs = data.get_data(
        "enrolment", "_id", [d.get("student_id") for d in assessment_docs])
    store_data = {
        "enrolment_docs": enrolment_docs,
        "assessment_subject_cohort": (assessment, subject, cohort)
    }
    return (cohort, cohort_items, subject, subject_items, assessment_items,
            store_data)
