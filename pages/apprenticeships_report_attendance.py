import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
from app import app
import app_data

attendance_table = dash_tabulator.DashTabulator(
        id={
                "section": "apprenticeships",
                "page": "reports",
                "tab": "attendance",
                "type": "table",
                "name": "attendance"
            },
        theme='bootstrap/tabulator_bootstrap4',
        options={
            "resizableColumns": False,
            "height": "70vh",
            "clipboard": "copy",
            "layout": "fitData"
        },
        columns=[
        {
            "title": "Student ID",
            "field": "Student ID",
            "visible": False,
            "clipboard": True
        },
            {
            "title": "Family name",
            "field": "Family name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
        {
            "title": "Given name",
            "field": "Given name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
             {
            "title": "All time sessions",
            "field": "All time sessions",
            "visible": False,
                "clipboard": True,
        },
    {
            "title": "All time present",
            "field": "All time present",
            "visible": False,
                "clipboard": True,
        },
   {
            "title": "All time late",
            "field": "All time late",
            "visible": False,
                "clipboard": True,
        },
    {
            "title": "All time attendance (%)",
            "field": "All time attendance (%)",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
            {
            "title": "All time punctuality (%)",
            "field": "All time punctuality (%)",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
             {
            "title": "90 day sessions",
            "field": "90 day sessions",
            "visible": False,
                "clipboard": True,
        },
    {
            "title": "90 day present",
            "field": "90 day present",
            "visible": False,
                "clipboard": True,
        },
   {
            "title": "90 day late",
            "field": "90 day late",
            "visible": False,
                "clipboard": True,
        },
             {
            "title": "90 day attendance (%)",
            "field": "90 day attendance (%)",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
            {
            "title": "90 day punctuality (%)",
            "field": "90 day punctuality (%)",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
                "clipboard": True,
        },
    ]    )

layout = dbc.Container([dbc.Row([dbc.Col([dcc.Loading(attendance_table)])])])


@app.callback(
   Output(
        {
            "section": "apprenticeships",
            "page": "reports",
            "tab": "attendance",
            "type": "table",
            "name": "attendance"
        }, "data"),
    [
            Input(
                {
                    "type": "storage",
                    "section": "apprenticeships",
                    "page": "reports",
                    "name": "attendance"
                }, 'data')
        ])
def update_table(attendance):
    attendance = attendance if isinstance(attendance, list) else [attendance]
    return (attendance)
 

