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

cohorts_table = dash_tabulator.DashTabulator(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "summary",
        "type": "table",
        "name": "cohorts"
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "height": "60vh",
        "clipboard": "copy",
        "layout": "fitData"
    }
)

# dbc.Row([dbc.Col([html.H5("Employer average")])]),
# dbc.Row([dbc.Col([html.Div(['Module grade'])], width=2),
#          dbc.Col([html.Div(id={
#              "section": "apprenticeships",
#              "page": "reports",
#              "tab": "summary",
#              "type": "div",
#              "name": "average mark"
#          })], width=1),
#          dbc.Col([html.Div(['90 day attendance (%)'])], width=3),
#          dbc.Col([html.Div(id={
#              "section": "apprenticeships",
#              "page": "reports",
#              "tab": "summary",
#              "type": "div",
#              "name": "average attendance"
#          })], width=1)]),
# dbc.Row([dbc.Col([html.H5("Cohort average")])]),

layout = dbc.Container([
    dbc.Row([dbc.Col([html.H4(id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "summary",
        "type": "heading",
        "name": "employer"
    })])]),
    dbc.Row([dbc.Col([html.Div(id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "summary",
        "type": "div",
        "name": "employer attendance"
    })])]),
    dbc.Row([dbc.Col([cohorts_table])])
], fluid=True)



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
                "type": "table",
                "name": "cohorts"
    }, 'columns'),
        Output({
            "section": "apprenticeships",
            "page": "reports",
            "tab": "summary",
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
def update_summary(learners, results, attendance, employer):

    learners_df = pd.DataFrame.from_records(learners, index='student_id')
    learners_df['cohort'] = pd.Categorical(learners_df['cohort'], categories=learners_df.sort_values('start_date', ascending=False)['cohort'].unique(), ordered=True)
    results_df = pd.merge(learners_df, pd.DataFrame.from_records(results, index='student_id'), left_index=True, right_index=True, how='left')
    attendance_df = pd.merge(learners_df, pd.DataFrame.from_records(attendance, index='Student ID'), left_index=True, right_index=True, how='left')

    employer_average_attendance = attendance_df[
        ['All time attendance (%)',
         'All time punctuality (%)',
         '90 day attendance (%)',
         '90 day punctuality (%)']].mean().apply(app_data.round_normal).to_frame().transpose()
    employer_attendance_table = dbc.Table.from_dataframe(employer_average_attendance)

    average_results_df = results_df.groupby('cohort')['mark'].mean().apply(app_data.round_normal).rename('Grade')
    average_attendance_df = attendance_df.groupby('cohort')[
        ['All time attendance (%)',
         'All time punctuality (%)',
         '90 day attendance (%)',
         '90 day punctuality (%)']].mean().sort_index(ascending=False).applymap(app_data.round_normal)
    merged_df = pd.merge(average_results_df, average_attendance_df, left_index=True, right_index=True).reset_index(names='Cohort')

    table_columns = [{'title': c, 'field': c, "headerFilter": True} for c in merged_df.columns]
    table_data = merged_df.to_dict(orient='records')

    return employer, employer_attendance_table, table_columns, table_data
