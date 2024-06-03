import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
from icecream import ic

from app import app
import app_data

attendance_table = dash_tabulator.DashTabulator(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "attendance",
        "type": "table",
        "name": "attendance"
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "height": "70vh",
        "clipboard": "copy",
        "layout": "fitData"
    },
)

layout = dbc.Container([dbc.Row([dbc.Col([
    dcc.Loading(attendance_table)
])])])


@app.callback(
    [
        Output(
            {
                "section": "apprenticeships",
                "page": "reports",
                "tab": "attendance",
                "type": "table",
                "name": "attendance"
            }, "columns"),
        Output(
        {
            "section": "apprenticeships",
            "page": "reports",
            "tab": "attendance",
            "type": "table",
            "name": "attendance"
        }, "data"),
    ],
    [
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "reports",
                "name": "learners"
            }, 'data'),
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "reports",
                "name": "attendance"
            }, 'data'),
    ])
def update_table(learners, attendance):
    if not learners:
        return [], []

    attendance = attendance if isinstance(attendance, list) else [attendance]

    learners_df = pd.DataFrame.from_records(learners).set_index('student_id')

    learner_cohorts = learners_df[['start_date', 'cohort']].sort_values('start_date', ascending=False)['cohort'].unique()

    attendance_df = pd.DataFrame.from_records(attendance).set_index('Student ID').applymap(app_data.round_normal)

    learners_attendance_df = pd.merge(learners_df, attendance_df, left_index=True, right_index=True)

    learners_attendance = learners_attendance_df.reset_index(names='student_id').to_dict(orient='records')

    table_columns=[
        {
            "title": "Student ID",
            "field": "student_id",
            "frozen": True,
            "visible": False,
            "clipboard": True
        },
        {
            "title": "Given name",
            "field": "given_name",
            "frozen": True,
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
            "clipboard": True,
        },
        {
            "title": "Family name",
            "field": "family_name",
            "frozen": True,
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
            "clipboard": True,
        },
        {
            "title": "Cohort",
            "field": "cohort",
            "headerFilter": 'select',
            "headerFilterParams": {
                "values": learner_cohorts
            },
            "headerFilterPlaceholder": "filter",
            "clipboard": True,
            "frozen": True
        },
        {
            "title": "Status",
            "field": "status",
            "headerFilter": 'select',
            "headerFilterParams": {
                "values": learners_df['status'].unique()
            },
            "headerFilterPlaceholder": "filter",
            "clipboard": True,
            "frozen": True
        },
        {
            "title": "All time sessions",
            "field": "All time sessions",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "All time present",
            "field": "All time present",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "All time late",
            "field": "All time late",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "All time attendance (%)",
            "field": "All time attendance (%)",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
            "clipboard": True,
        },
        {
            "title": "All time punctuality (%)",
            "field": "All time punctuality (%)",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
            "clipboard": True,
        },
        {
            "title": "90 day sessions",
            "field": "90 day sessions",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "90 day present",
            "field": "90 day present",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "90 day late",
            "field": "90 day late",
            "visible": False,
            "clipboard": True,
        },
        {
            "title": "90 day attendance (%)",
            "field": "90 day attendance (%)",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
            "clipboard": True,
        },
        {
            "title": "90 day punctuality (%)",
            "field": "90 day punctuality (%)",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
            "clipboard": True,
        },
    ]
    return table_columns, learners_attendance
