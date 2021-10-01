import dash_tabulator
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

# Attendance tab content
attendance_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "attendance"
    },
    options={
        "resizableColumns": False,
        # "layout": "fitData",
        # "maxHeight": "70vh",
        "clipboard": "copy"
    },
    theme='bootstrap/tabulator_bootstrap4',
)
layout = dbc.Container(attendance_table)

@app.callback(
    [
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "attendance"
        }, "columns"),
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "attendance"
        }, "data"),
   ],
    [
        Input("sixthform-pastoral-store", "data")
    ],
)
def update_pastoral_attendance(store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    attendance_docs = store_data.get('attendance_docs')
    if not attendance_docs:
        return [], []
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        'date > @this_year_start')
    weekly_df = attendance_df.query("subtype == 'weekly'")
    # Merge on student id
    merged_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                         weekly_df,
                         left_on='_id',
                         right_on='student_id',
                         how='left')
    # Get per student totals
    cumulative_df = merged_df.groupby("student_id").sum().reset_index()
    cumulative_df['cumulative_percent_present'] = round(
        100 * cumulative_df['actual'] / cumulative_df['possible'])
    # Calculate percent present
    merged_df['percent_present'] = round(100 * merged_df['actual'] /
                                         merged_df['possible'])
    # Pivot to bring dates to columns
    attendance_pivot = merged_df.set_index(
        ["student_id", "given_name", "family_name",
         "date"])["percent_present"].unstack().reset_index()
    # Add the cumulative column
    attendance_pivot = pd.merge(
        attendance_pivot,
        cumulative_df[["student_id", "cumulative_percent_present"]],
        how='left',
        left_on="student_id",
        right_on="student_id",
        suffixes=("", "_y"))
    columns = [
        {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
        },
        {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
        },
    ]
    columns.extend([
        {
            #"name": data.format_date(d),
            "title": "This week",
            "field": d,
            "headerHozAlign": "right",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        } for d in attendance_pivot.columns[-2:-1]
    ])
    columns.append({
        "title": "This year",
        "field": "cumulative_percent_present",
        "headerHozAlign": "right",
        "hozAlign": "right",
        "headerFilter": True,
        "headerFilterFunc": "<",
        "headerFilterPlaceholder": "Less than",
    })

    return columns, attendance_pivot.to_dict(orient='records')
