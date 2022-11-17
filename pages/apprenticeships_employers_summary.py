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
import app_data
import dash_bootstrap_components as dbc

cohort_dropdown = dbc.Select(id={
    "section": "apprenticeships",
    "page": "employers",
    "tab": "summary",
    "type": "dropdown",
    "name": "cohort"
}, )

results_table = html.Div(
    id={
        "section": "apprenticeships",
        "page": "employers",
        "tab": "summary",
        "type": "table",
        "name": "results"
    })
layout = dbc.Container([
    dbc.Row([dbc.Col([cohort_dropdown])]),
    dbc.Row([dbc.Col([results_table])])
])


@app.callback(
    [
        Output(
            {
                "section": "apprenticeships",
                "page": "employers",
                "tab": "summary",
                "type": "dropdown",
                "name": "cohort"
            }, "value"),
        Output(
            {
                "section": "apprenticeships",
                "page": "employers",
                "tab": "summary",
                "type": "dropdown",
                "name": "cohort"
            }, "options"),
    ],
    [
        Input(
            {
                "section": "apprenticeships",
                "type": "storage",
                "page": "employers",
                "name": "students"
            }, "data")
    ],[
            State(
                {
                    "section": "apprenticeships",
                    "page": "employers",
                    "type": "dropdown",
                    "name": "employer"
                }, "label")
        ]
)
def update_cohort_dropdown(store_data, employer):
    if not store_data:
        return [html.H4("No students with this employer")]

    student_df = pd.DataFrame.from_records(store_data)
    cohorts = app_data.get_cohorts_by_employer(employer)
    cohort_options = [{'label': c, 'value': c} for c in cohorts]
    cohort_value = cohort_options[0].get('value')
    return cohort_value, cohort_options


@app.callback(
    Output(
        {
            "section": "apprenticeships",
            "page": "employers",
            "tab": "summary",
            "type": "table", 
            "name": "results"
        }, "children"), [
            Input(
                {
                    "section": "apprenticeships",
                    "page": "employers",
                    "tab": "summary",
                    "type": "dropdown",
                    "name": "cohort"
                }, "value"),
        ], [
            State(
                {
                    "section": "apprenticeships",
                    "page": "employers",
                    "type": "dropdown",
                    "name": "employer"
                }, "label")
        ])
def update_table(cohort, employer):
    results = app_data.get_results_for_cohort_employer(cohort, employer)
    if not results:
        return "No results for these learners."
    results_df = pd.DataFrame.from_records(results)
    results_df['Class'] = pd.Categorical(
        results_df['total'].fillna(-1).apply(lambda t: get_class(t)),
        ['TBA', 'Fail', 'Pass', 'Merit', 'Distinction'])
    grouped_df = results_df.groupby(
        ['Level', 'Module'], observed=True)['Class'].value_counts().unstack(-1)
    return dbc.Table.from_dataframe(grouped_df.reset_index())


def get_class(mark):
    if mark >= 69.5:
        return 'Distinction'
    elif mark >= 59.5:
        return 'Merit'
    elif mark >= 39.5:
        return 'Pass'
    elif mark >= 0:
        return 'Fail'
    else:
        return 'TBA'
