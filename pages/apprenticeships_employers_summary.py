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
    ],
)
def update_cohort_dropdown(store_data):
    if not store_data:
        return [html.H4("No students with this employer")]

    student_df = pd.DataFrame.from_records(store_data)
    cohorts = student_df['cohort_name'].sort_values().unique()
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
    results_df = pd.DataFrame.from_records(results)
    results_df['Class'] = pd.Categorical(
        results_df['total'].apply(lambda t: get_class(t)),
        ['Missing', 'Fail', 'Pass', 'Merit', 'Distinction'])
    grouped_df = results_df.groupby(
        ['Level', 'Module'], observed=True)['Class'].value_counts().unstack(-1)
    print(grouped_df)
    # grouped_df = results_df.pivot_table(index=['Level', 'Module'], columns='Class', values='student_id', aggfunc='count')
    return dbc.Table.from_dataframe(grouped_df.reset_index())


def get_class(mark):
    if mark is not None:
        if mark >= 69.5:
            return 'Distinction'
        elif mark >= 59.5:
            return 'Merit'
        elif mark >= 39.5:
            return 'Pass'
        else:
            return 'Fail'
    else:
        return 'Missing'