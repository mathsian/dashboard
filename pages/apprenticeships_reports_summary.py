import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np

import data
from app import app
import app_data
from icecream import ic


layout = dcc.Loading(dbc.Container([
    dbc.Row([dbc.Col([
        html.H2(id={
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "heading",
            "name": "employer"
        }),
        html.H4("Learners by status"),
        html.Div(id={
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "div",
            "name": "employer status"
        }),
        html.H4("Attendance"),
        html.Div(id={
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "div",
            "name": "employer attendance"
        }),
        html.H4("Module grade profile"),
        dcc.Graph(id={
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "graph",
            "name": "grade profile"
        },
            config={
                "displayModeBar": False,
                "staticPlot": True,
            },
            figure={
                "layout": {
                    "xaxis": {
                        "visible": False
                    },
                    "yaxis": {
                        "visible": False
                    },
                    "height": 200,
                }
            }
        )
    ])]),

]))


@app.callback(
    [
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "heading",
            "name": "employer"
        }, 'children'),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "div",
            "name": "employer attendance"
        }, 'children'),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "div",
            "name": "employer status"
        }, 'children'),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
            "type": "graph",
            "name": "grade profile"
        }, 'figure'),
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
                "name": "results"
            }, 'data'),
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "reports",
                "name": "attendance"
            }, 'data')
    ],
    [
        State({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, 'label')
    ]
)
def update_summary(learners, results, attendance, employer):
    learners_df = pd.DataFrame.from_records(learners, index='student_id')
    learners_df['cohort'] = pd.Categorical(learners_df['cohort'],
                                           categories=learners_df.sort_values('start_date', ascending=False)[
                                               'cohort'].unique(), ordered=True)

    results_df = pd.merge(learners_df, pd.DataFrame.from_records(results, index='student_id'), left_index=True,
                          right_index=True, how='left')
    grade_profile_fig = app_data.graph_grade_profile(results_df, 'mark')
    grade_profile_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    attendance_df = pd.merge(learners_df, pd.DataFrame.from_records(attendance, index='Student ID'), left_index=True,
                             right_index=True, how='left')

    employer_average_attendance = attendance_df[
        ['All time attendance (%)',
         'All time punctuality (%)',
         '90 day attendance (%)',
         '90 day punctuality (%)']].mean().apply(app_data.round_normal).to_frame().transpose()
    employer_attendance_table = dbc.Table.from_dataframe(employer_average_attendance)

    employer_status = learners_df['status'].value_counts().to_frame().transpose()
    employer_status_table = dbc.Table.from_dataframe(employer_status)


    return employer, employer_attendance_table, employer_status_table, grade_profile_fig
