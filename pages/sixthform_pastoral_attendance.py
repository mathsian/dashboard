import filters
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
        "layout": "fitData",
        "maxHeight": "70vh",
        "clipboard": "copy"
    },
    theme='bootstrap/tabulator_bootstrap4',
)

gauge_last = daq.Gauge(
    id={
        "type": "gauge",
        "section": "sixthform",
        "page": "pastoral",
        "tab": "attendance",
        "name": "last_week"
    },
    label="This week",
    scale={
        "start": 0,
        "interval": 10,
        "labelInterval": 2,
    },
    size=180,
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
),
gauge_overall = daq.Gauge(
    id={
        "type": "gauge",
        "section": "sixthform",
        "page": "pastoral",
        "tab": "attendance",
        "name": "overall"
    },
    label="This year",
    scale={
        "start": 0,
        "interval": 10,
        "labelInterval": 2,
    },
    size=180,
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
)

layout = dbc.Row([
    dbc.Col([
        dbc.Row([
            dbc.Col(gauge_last),
            dbc.Col(gauge_overall)
        ])
    ]),
     dbc.Col(attendance_table)
    ])


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
        Output(
            {
                "type": "gauge",
        "section": "sixthform",
                "page": "pastoral",
                "tab": "attendance",
                "name": "last_week",
            }, "value"),
        Output(
            {
                "type": "gauge",
        "section": "sixthform",
                "page": "pastoral",
                "tab": "attendance",
                "name": "overall",
            }, "value"),
    ],
    [
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
    ],
)
def update_pastoral_attendance(filter_value):
    cohort, team = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], [], 0, 0
    student_ids = [s.get('_id') for s in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    if not attendance_docs:
        return [], [], 0, 0
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        'date > @this_year_start')
    weekly_df = attendance_df.query("subtype == 'weekly'")
    last_week_date = weekly_df["date"].max()
    overall_totals = weekly_df.sum()
    last_week_totals = weekly_df.query("date == @last_week_date").sum()
    overall_percent = round(
        100 * overall_totals['actual'] / overall_totals['possible'], 1)
    last_week_percent = round(
        100 * last_week_totals['actual'] / last_week_totals['possible'], 1)
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
            "title": d,
            "field": d,
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        } for d in attendance_pivot.columns[-2:-1]
    ])
    columns.append({
        "title": "Year",
        "field": "cumulative_percent_present",
        "hozAlign": "right",
        "headerFilter": True,
        "headerFilterFunc": "<",
        "headerFilterPlaceholder": "Less than",
    })

    return columns, attendance_pivot.to_dict(
        orient='records'), last_week_percent, overall_percent
