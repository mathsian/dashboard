import dash_tabulator
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

# Kudos tab content
kudos_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "section": "sixthform",
        "page": "pastoral",
        "name": "kudos",
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "height": "70vh",
        "pagination": "local",
        "clipboard": "copy",
        "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}, {"column": "total", "dir": "desc"}]
    },
    columns=[
        {
            "field": "given_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
        },
        {
            "field": "family_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
        },
    ] + [{
        "title": v,
        "field": v,
        "sorter": "number",
        "headerHozAlign": "right",
        "hozAlign": "right",
        "topCalc": "sum"
    } for v in curriculum.values] + [{
        "title": "Total",
        "field": "total",
        "sorter": "number",
        "headerHozAlign": "right",
        "hozAlign": "right",
        "topCalc": "sum"
    }],
)

layout = dbc.Row(dbc.Col(dcc.Loading(kudos_table)))

@app.callback(
    Output(
        {
            "type": "table",
            "section": "sixthform",
            "page": "pastoral",
            "name": "kudos",
        }, "data"), [
            Input("sixthform-pastoral-store", "data"),
        ])
def update_pastoral_kudos(store_data):
    kudos_pivot_docs = store_data.get('kudos_pivot_docs')
    if not kudos_pivot_docs:
        return []
    return kudos_pivot_docs
