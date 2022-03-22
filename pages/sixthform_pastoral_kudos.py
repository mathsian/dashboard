import filters
import dash_tabulator
import dash_core_components as dcc
import dash_html_components as html
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
#        "layout": "fitData",
#        "maxHeight": "60vh",
        "clipboard": "copy"
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
        "headerHozAlign": "right",
        "hozAlign": "right",
        "topCalc": "sum"
    } for v in curriculum.values] + [{
        "title": "Total",
        "field": "total",
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
