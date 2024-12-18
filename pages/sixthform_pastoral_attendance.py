import dash_tabulator
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from datetime import date, timedelta
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
        "clipboard": "copy",
        "height": "70vh",
        "pagination": "local",
        "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}]
    },
    theme='bootstrap/tabulator_bootstrap4',
)
layout = dbc.Container(
    dcc.Loading(attendance_table)
    )


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
    term_date = store_data.get('term_date')
    if not attendance_docs:
        return [], []
    this_year_start = term_date['year_start']
    term_start = term_date['term_start']
    attendance_df = pd.DataFrame.from_records(attendance_docs).query('date >= @this_year_start')
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
    # Get per student term totals
    term_cumulative_df = merged_df.query('date >= @term_start').groupby("student_id").sum().reset_index()
    term_cumulative_df['term_cumulative_percent_present'] = round(
        100 * term_cumulative_df['actual'] / term_cumulative_df['possible'])
    # Calculate percent present for recent weeks
    three_weeks_ago = (date.today() - timedelta(weeks=3)).isoformat()
    merged_df.query('date > @three_weeks_ago', inplace=True)
    merged_df['percent_present'] = round(100 * merged_df['actual'] /
                                         merged_df['possible'])
    # Pivot to bring dates to columns
    attendance_pivot_a = merged_df.set_index(
        ["student_id", "student_email", "given_name", "family_name",
         "date"])["percent_present"].unstack().reset_index()
    # Add the term cumulative column
    attendance_pivot_b = pd.merge(
        attendance_pivot_a,
        term_cumulative_df[["student_id", "term_cumulative_percent_present"]],
        how='left',
        left_on="student_id",
        right_on="student_id",
        suffixes=("", "_z"))
    # Add the cumulative column
    attendance_pivot = pd.merge(
        attendance_pivot_b,
        cumulative_df[["student_id", "cumulative_percent_present"]],
        how='left',
        left_on="student_id",
        right_on="student_id",
        suffixes=("", "_y"))
    columns = [
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Email",
            "field": "student_email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
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
            "title": data.format_date(d),
            "field": d,
            "sorter": "number",
            "headerHozAlign": "right",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        } for d in attendance_pivot.columns[4:-2]
    ])
    columns.append({
        "title": "This term",
        "field": "term_cumulative_percent_present",
        "sorter": "number",
        "headerHozAlign": "right",
        "hozAlign": "right",
        "headerFilter": True,
        "headerFilterFunc": "<",
        "headerFilterPlaceholder": "Less than",
    })
    columns.append({
        "title": "This year",
        "field": "cumulative_percent_present",
        "sorter": "number",
        "headerHozAlign": "right",
        "hozAlign": "right",
        "headerFilter": True,
        "headerFilterFunc": "<",
        "headerFilterPlaceholder": "Less than",
    })
    return columns, attendance_pivot.sort_values('cumulative_percent_present').to_dict(orient='records')
