import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from plotly import graph_objects as go
import data
from app import app
import app_data
from icecream import ic

cohorts_table = dash_tabulator.DashTabulator(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "cohorts",
        "type": "table",
        "name": "cohorts"
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "clipboard": "copy",
        "layout": "fitData",
        "pagination": "local",
        "paginationSize": 8
    },
)

volumes_graph = dcc.Graph(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "cohorts",
        "type": "graph",
        "name": "volumes"
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
            "height": 320,
        }
    }
)

layout = dbc.Row([dbc.Col([
    dcc.Loading(html.H2(id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "cohorts",
        "type": "heading",
        "name": "employer"
    })),
    html.H4('Performance'),
    dcc.Loading(cohorts_table),
    html.H4('Status'),
    dcc.Loading(volumes_graph),
])])

@app.callback(
    [
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "cohorts",
            "type": "heading",
            "name": "employer"
        }, "children"),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "cohorts",
            "type": "graph",
            "name": "volumes"
        }, "figure"),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "cohorts",
            "type": "table",
            "name": "cohorts"
        }, 'columns'),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "cohorts",
            "type": "table",
            "name": "cohorts"
        }, 'data'),
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


def update_cohorts_tab(learners, results, attendance, employer):
    learners_df = pd.DataFrame.from_records(learners, index='student_id')

    volumes_fig = app_data.graph_learner_volumes(learners_df)

    learners_df['cohort'] = pd.Categorical(learners_df['cohort'],
                                           categories=learners_df.sort_values('start_date', ascending=False)[
                                               'cohort'].unique(), ordered=True)


    results_df = pd.merge(learners_df, pd.DataFrame.from_records(results, index='student_id'), left_index=True,
                          right_index=True, how='left')

    attendance_df = pd.merge(learners_df, pd.DataFrame.from_records(attendance, index='Student ID'), left_index=True,
                             right_index=True, how='left')

    status_df = learners_df.reset_index()[['cohort', 'status', 'student_id']].pivot_table(index='cohort',
                                                                                          columns='status',
                                                                                          aggfunc='count')
    status_df.columns = status_df.columns.get_level_values(1)

    average_results_df = results_df.groupby('cohort')['mark'].mean().apply(app_data.round_normal).rename('Grade')
    average_attendance_df = attendance_df.groupby('cohort')[
        ['All time attendance (%)',
         'All time punctuality (%)',
         '90 day attendance (%)',
         '90 day punctuality (%)']].mean().sort_index(ascending=False).applymap(app_data.round_normal)

    counts_df = learners_df.reset_index()[['cohort', 'student_id']].groupby('cohort').count().rename(
        {'student_id': 'count'}, axis=1)

    merged_df = pd.merge(counts_df, status_df, left_index=True, right_index=True)
    merged_df = pd.merge(average_results_df, merged_df, left_index=True, right_index=True)
    merged_df = pd.merge(average_attendance_df, merged_df, left_index=True, right_index=True).reset_index()

    merged_df = merged_df[['cohort']].apply(lambda row: pd.Series(app_data.parse_cohort(row['cohort'])), axis=1).join(
        merged_df)

    merged_df.sort_values(['year', 'intake', 'short'], ascending=[False, True, True], inplace=True)

    table_columns = [
        {'title': 'Year', 'field': 'year', 'headerFilter': 'select',
         'headerFilterParams': merged_df['year'].sort_values().unique(), 'frozen': True},
        {'title': 'Intake', 'field': 'intake', 'headerFilter': 'select',
         'headerFilterParams': merged_df['intake'].unique(), 'frozen': True},
        {'title': 'Programme', 'field': 'short', 'headerFilter': 'select',
         'headerFilterParams': merged_df['short'].sort_values().unique(), 'frozen': True},
        {'title': 'Grade', 'field': 'Grade', 'headerFilter': True, 'hozAlign': 'right', 'headerFilterFunc': '<',
         'headerFilterPlaceholder': 'Less than'},
        {'title': 'All time attendance (%)', 'field': 'All time attendance (%)', 'hozAlign': 'right',
         'headerFilter': True, 'headerFilterFunc': '<',
         'headerFilterPlaceholder': 'Less than'},
        {'title': 'All time punctuality (%)', 'field': 'All time punctuality (%)', 'hozAlign': 'right',
         'headerFilter': True, 'headerFilterFunc': '<',
         'headerFilterPlaceholder': 'Less than'},
        {'title': '90 day attendance (%)', 'field': '90 day attendance (%)', 'hozAlign': 'right', 'headerFilter': True,
         'headerFilterFunc': '<',
         'headerFilterPlaceholder': 'Less than'},
        {'title': '90 day punctuality (%)', 'field': '90 day punctuality (%)', 'hozAlign': 'right',
         'headerFilter': True, 'headerFilterFunc': '<',
         'headerFilterPlaceholder': 'Less than'},
        {'title': 'Count', 'field': 'count', 'hozAlign': 'right'},
        {'title': 'Continuing', 'field': 'Continuing', 'hozAlign': 'right'},
        {'title': 'Completed', 'field': 'Completed', 'hozAlign': 'right'},
        {'title': 'BiL', 'field': 'Break in learning', 'hozAlign': 'right'},
        {'title': 'Withdrawn', 'field': 'Withdrawn', 'hozAlign': 'right'},
    ]

    table_data = merged_df.to_dict(orient='records')

    return employer, volumes_fig, table_columns, table_data
