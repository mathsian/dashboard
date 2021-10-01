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

# Weekly tab content
weekly_header = html.H4(children=[
    "Week beginning ",
    html.Span(id={
        "type": "text",
        "page": "pastoral",
        "tab": "weekly",
        "name": "wb"
    })
])

weekly_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "weekly"
    },
    options={
        "resizableColumns": False,
        # "layout": "fitData",
        # "maxHeight": "70vh",
        "clipboard": "copy"
    },
    columns=[
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
        {
            "title": "Present",
            "field": "pr",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        },
        {
            "title": "Authorised",
            "field": "au",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
        {
            "title": "Unauthorised",
            "field": "un",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
        {
            "title": "Late",
            "field": "la",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
)
weekly_picker = dcc.DatePickerSingle(
    id={
        "type": "picker",
        "page": "pastoral",
        "tab": "weekly"
    },
    date=date.today(),
    display_format="MMM DD YY",
)

layout = [
    dbc.Row([
            dbc.Col(width=3, children=weekly_picker),
            dbc.Col(weekly_header)
        ]),
    dbc.Row(
        dbc.Col(weekly_table)
    )
]


@app.callback([
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "weekly"
    }, "data"),
    Output({
        "type": "text",
        "page": "pastoral",
        "tab": "weekly",
        "name": "wb"
    }, "children"),
], [
    Input("sixthform-pastoral-store", "data"),
    Input({
        "type": "picker",
        "page": "pastoral",
        "tab": "weekly"
    }, "date")
])
def update_weekly_table(store_data, picker_value):
    enrolment_docs = store_data.get('enrolment_docs')
    attendance_docs = store_data.get('attendance_docs')
    enrolment_df = pd.DataFrame.from_records(enrolment_docs)
    # Get attendance for the latest week before the chosen date
    attendance_df = pd.DataFrame.from_records(attendance_docs).query("subtype == 'weekly'").query("date <= @picker_value").query("date == date.max()")
    # Picked too early a date?
    if attendance_df.empty:
        attendance_df = pd.DataFrame.from_records(
            data.get_data("attendance", "student_id",
                          student_ids)).query("date == date.min()")
    attendance_df.eval("pr = 100*actual/possible", inplace=True)
    attendance_df.eval("un = 100*unauthorised/possible", inplace=True)
    attendance_df.eval("au = 100*authorised/possible", inplace=True)
    attendance_df.eval("la = 100*late/actual", inplace=True)
    merged_df = pd.DataFrame.merge(enrolment_df,
                                   attendance_df.round(),
                                   how='left',
                                   left_on='_id',
                                   right_on='student_id')
    return merged_df.to_dict(orient='records'), data.format_date(
        attendance_df["date"].iloc[0])

