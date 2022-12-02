import dash_tabulator
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import datetime, timedelta

from app import app
import data
import curriculum

# Concern tab content
# concern_table = dash_tabulator.DashTabulator(
#     id={
#         "type": "table",
#         "page": "pastoral",
#         "tab": "concern",
#     },
#     columns=[
#         {
#             "title": "Student ID",
#             "field": "student_id",
#             "visible": False,
#             "clipboard": "true",
#             "download": "true"
#         },
#         {
#             "title": "Email",
#             "field": "student_email",
#             "visible": False,
#             "clipboard": "true",
#             "download": "true"
#         },
#         {
#             "title": "Date",
#             "field": "date",
#             "width": "10%"
#         },
#         {
#             "title": "Given name",
#             "field": "given_name",
#             "width": "10%",
#             "headerFilter": True,
#             "headerFilterPlaceholder": "filter",
#         },
#         {
#             "title": "Family name",
#             "field": "family_name",
#             "width": "15%",
#             "headerFilter": True,
#             "headerFilterPlaceholder": "filter",
#         },
#         {
#             "title": "Category",
#             "field": "category",
#             "width": "10%",
#             "headerFilter": "select",
#             "headerFilterParams": {
#                 "values": curriculum.concern_categories
#             },
#             "headerFilterPlaceholder": "filter",
#         },
#         {
#             "title": "Stage",
#             "field": "stage",
#             "width": "10%",
#             "headerFilter": "select",
#             "headerFilterParams": {
#                 "values": curriculum.concern_stages
#             },
#             "headerFilterPlaceholder": "filter",
#         },
#         {
#             "title": "Description",
#             "field": "description",
#             "formatter": "plaintext",
#             "headerFilter": True,
#             "headerFilterPlaceholder": "filter",
#         },
#         {
#             "title": "Additional",
#             "field": "discrimination",
#             "width": "10%",
#             "headerFilter": "select",
#             "headerFilterParams": {
#                 "values": curriculum.concern_discrimination
#             },
#             "headerFilterPlaceholder": "filter",
#         },
#        {
#             "title": "Raised by",
#             "field": "from",
#            "width": "10%",
#            "headerFilter": True,
#            "headerFilterPlaceholder": "filter",
#         },
#     ],
#     theme='bootstrap/tabulator_bootstrap4',
#     options={
#         "resizableColumns": False,
#         # "layout": "fitDataStretch",
#         # "maxHeight": "70vh",
#         "clipboard": "copy",
#         "height": "70vh",
#         "pagination": "local",
#         "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}, {"column": "date", "dir": "desc"}]
#     },
# )

concern_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
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
            "title": "10 days",
            "field": "ten",
            "width": "15%",
            "sorter": "number",
            "headerHozAlign": "right",
            "hozAlign": "right",
            "topCalc": "sum"
        },
        {
            "title": "30 days",
            "field": "thirty",
            "width": "15%",
            "sorter": "number",
            "headerHozAlign": "right",
            "hozAlign": "right",
            "topCalc": "sum"
        },
          {
            "title": "This year",
            "field": "year",
            "width": "15%",
            "sorter": "number",
            "headerHozAlign": "right",
            "hozAlign": "right",
            "topCalc": "sum"
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
        "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}, {"column": "ten", "dir": "desc"}]
    },
)

layout = dbc.Container(dcc.Loading(concern_table))


@app.callback(
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
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

    this_year_start = curriculum.this_year_start
    year_df = pd.DataFrame.from_records(concern_docs).query("date >= @this_year_start")[["student_id", "date"]]
    thirty_days_ago = datetime.isoformat(datetime.today() - timedelta(days=30))
    thirty_df = year_df.query("date >= @thirty_days_ago")
    ten_days_ago = datetime.isoformat(datetime.today() - timedelta(days=10))
    ten_df = thirty_df.query("date >= @ten_days_ago")
    print(ten_df)
    year_sum = year_df.groupby("student_id").count().rename(columns={"date": "year"})
    thirty_sum = thirty_df.groupby("student_id").count().rename(columns={"date": "thirty"})
    ten_sum = ten_df.groupby("student_id").count().rename(columns={"date": "ten"})
    print(ten_sum)
    concern_df = pd.merge(
        pd.DataFrame.from_records(enrolment_docs).set_index("_id"),
        pd.merge(
            year_sum,
            pd.merge(
                thirty_sum,
                ten_sum,
                how='left',
                left_index=True,
                right_index=True),
            how='left',
            left_index=True,
            right_index=True),
        how='left',
        left_index=True,
        right_index=True).fillna(0).sort_values("ten", ascending=False)
    return concern_df.to_dict(orient="records")
