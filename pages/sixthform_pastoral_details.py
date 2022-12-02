import dash_tabulator
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

# Concern tab content
concern_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "details",
    },
    columns=[
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
            "title": "Date",
            "field": "date",
            "width": "10%"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "15%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Category",
            "field": "category",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_categories
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Stage",
            "field": "stage",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_stages
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Description",
            "field": "description",
            "formatter": "plaintext",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Additional",
            "field": "discrimination",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_discrimination
            },
            "headerFilterPlaceholder": "filter",
        },
       {
            "title": "Raised by",
            "field": "from",
           "width": "10%",
           "headerFilter": True,
           "headerFilterPlaceholder": "filter",
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        # "layout": "fitDataStretch",
        # "maxHeight": "70vh",
        "clipboard": "copy",
        "height": "70vh",
        "pagination": "local",
        "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}, {"column": "date", "dir": "desc"}]
    },
)

layout = dbc.Container(dcc.Loading(concern_table))


@app.callback(
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "details",
    }, "data"),
    [
        Input("sixthform-pastoral-store", "data"),
    ],
)
def update_pastoral_concern(store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    concern_docs = store_data.get('concern_docs')
    if not concern_docs:
        return []
    concern_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                          pd.DataFrame.from_records(concern_docs),
                          how="right",
                          left_on="_id",
                          right_on="student_id").sort_values("date",
                                                             ascending=False)
    this_year_start = curriculum.this_year_start
    return concern_df.query("date >= @this_year_start").to_dict(orient="records")
