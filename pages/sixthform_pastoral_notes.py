import dash_tabulator
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from datetime import datetime, timedelta
from app import app

notes_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "notes",
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
            "width": "15%",
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
            "title": "Date",
            "field": "date",
            "width": "15%",
            "sorter": "number",
            "headerHozAlign": "right",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Category",
            "field": "category",
            "width": "15%",
            "headerFilter": 'select',
            "headerFilterParams": {
                "values": ['Absence', 'Lateness']
            },
            "headerFilterPlaceholder": "filter",
            "clipboard": True,
        },
        {
            "title": "Comment",
            "field": "comment",
        },
        {
            "title": "Include in report",
            "field": "report",
            "align": "center",
            "formatter": "tickCross",
        }
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

layout = dbc.Container(dcc.Loading(notes_table))


@app.callback(
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "notes",
    }, "data"),
    [
        Input("sixthform-pastoral-store", "data"),
    ],
)
def update_pastoral_notes(store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    note_docs = store_data.get('note_docs')
    if not note_docs:
        return []
    note_df = pd.merge(
        pd.DataFrame.from_records(enrolment_docs).set_index("_id"),
        pd.DataFrame.from_records(note_docs).set_index("student_id"),
        left_index=True,
        right_index=True)
    return note_df.to_dict(orient="records")
