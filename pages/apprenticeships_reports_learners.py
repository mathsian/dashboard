import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from app import app
import app_data
from icecream import ic

learners_table = dash_tabulator.DashTabulator(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "results",
        "type": "table",
        "name": "learners"
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "height": "70vh",
        "clipboard": "copy",
        "layout": "fitData"
    }
)

layout = dbc.Container([dbc.Row([dbc.Col([dcc.Loading(learners_table)])])])


@app.callback(
    [
        Output(
            {
                "section": "apprenticeships",
                "page": "reports",
                "tab": "results",
                "type": "table",
                "name": "learners"
            }, "columns"),
        Output(
            {
                "section": "apprenticeships",
                "page": "reports",
                "tab": "results",
                "type": "table",
                "name": "learners"
            }, "data"),
    ], [
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
            }, 'data'),
    ])
def update_table(learners, results, attendance):

    if not learners:
        return [], []

    learner_columns = ['student_id', 'college_email', 'cohort', 'start_date', 'given_name', 'family_name', 'status']

    learners_df = pd.DataFrame.from_records(learners, columns=learner_columns, index='student_id')

    learner_cohorts = learners_df[['start_date', 'cohort']].sort_values('start_date', ascending=False)[
        'cohort'].unique()
    results_df = pd.DataFrame.from_records(results)

    # Learners with no results will have NaN under short
    results_df['short'].fillna('No results yet', inplace=True)

    results_df = unpivot_results(results_df)

    # Now we can drop the No results yet column
    results_df.drop('No results yet', level='short', axis='columns', inplace=True, errors='ignore')

    group_columns = [
        {"title": level,
         "columns": [
             {
                 "title": short,
                 "field": short,
                 "clipboard": True,
                 "headerTooltip": name,
             } for (name, short) in results_df[('mark', level,)].columns
         ]} for level in results_df.columns.unique(1)
    ]

    # flatten multiindex
    results_df.columns = [s for m, l, n, s in results_df.columns]

    # merge with biographic
    learner_results_df = pd.merge(learners_df, results_df, left_index=True, right_index=True)

    # merge with attendance
    attendance_df = pd.DataFrame.from_records(attendance).set_index('Student ID').applymap(app_data.round_normal)
    learner_results_attendance_df = pd.merge(learner_results_df, attendance_df, left_index=True, right_index=True)

    columns = [
                  {
                      "title": "Student ID",
                      "field": "student_id",
                      "headerFilter": True,
                      "headerFilterPlaceholder": "search",
                      "frozen": True,
                      "clipboard": True,
                      "visible": False,
                  },
                  {
                      "title": "Email",
                      "field": "college_email",
                      "headerFilter": True,
                      "headerFilterPlaceholder": "search",
                      "frozen": True,
                      "clipboard": True,
                      "visible": False,
                  },
                  {
                      "title": "Given name",
                      "field": "given_name",
                      "headerFilter": True,
                      "headerFilterPlaceholder": "search",
                      "clipboard": True,
                      "frozen": True
                  },
                  {
                      "title": "Family name",
                      "field": "family_name",
                      "headerFilter": True,
                      "headerFilterPlaceholder": "search",
                      "clipboard": True,
                      "frozen": True
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
              ] + group_columns + [{
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

    data = learner_results_attendance_df.reset_index(names='student_id').fillna('-').to_dict(orient='records')
    return columns, data


def unpivot_results(results_df):
    results_drop = ['code', 'credits']
    results_index = ['student_id', 'start_date', 'level', 'name', 'short']

    results_df.set_index(results_index, inplace=True)

    results_df.drop(results_drop, axis='columns', inplace=True)

    # Sort by start date of instances
    results_df.sort_index(level=['level', 'start_date'], inplace=True)
    # Then drop start_date because we don't want to distinguish instances of the same module
    results_df = results_df.droplevel(level='start_date')

    results_df = results_df.unstack(['level', 'name', 'short'])

    average_column = ('mark', 'All levels', 'Average grade', 'Average')
    results_df[average_column] = results_df.mean(axis=1).apply(app_data.round_normal)

    # move the average column to the front
    results_df.insert(0, average_column, results_df.pop(average_column))

    return results_df
