import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import app_data
import dash_bootstrap_components as dbc

layout = dbc.Row(
    dbc.Col(
        [html.H4(
            id={
                "section": "apprenticeships",
                "type": "heading",
                "page": "cohorts",
                "tab": "report",
                "name": "reports"
            }),
         dbc.Accordion(
  id={
                "section": "apprenticeships",
                "type": "accordion",
                "page": "cohorts",
                "tab": "report",
                "name": "reports"
            }
         )]
        ))


@app.callback([
    Output(
        {
            "section": "apprenticeships",
            "type": "heading",
            "page": "cohorts",
            "tab": "report",
            "name": "reports"
        }, "children"),
    Output(
        {
            "section": "apprenticeships",
            "type": "accordion",
            "page": "cohorts",
            "tab": "report",
            "name": "reports"
        }, "children"),
], [
    Input(
        {
            "section": "apprenticeships",
            "type": "storage",
            "page": "cohorts",
            "name": "selected"
        }, "data")
])
def update_student_report(store_data):
    if not store_data:
        return "Select a student to view their report", []
    accordion_items = []
    for student_id in store_data:
        student = app_data.get_student_by_id(student_id)
        results = app_data.get_results_for_student(student_id)
        actual_results = [
            r.get('total') for r in results if r.get('total') is not None
        ]
        if len(actual_results):
            average = round(sum(actual_results) / len(actual_results), 0)
        else:
            average = "-"
        accordion_item = dbc.AccordionItem(
            id={
                "type": "accordion_item",
                "section": "apprenticeships",
                "page": "cohorts",
                "tab": "report",
                "name": f'{student_id}'
            },
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Table([
                            html.Tr([
                                html.Td("Cohort"),
                                html.Td(student.get("cohort_name"))
                            ]),
                            html.Tr([
                                html.Td("Employer"),
                                html.Td(student.get("employer"))
                            ]),
                            html.Tr([
                                html.Td("Status"),
                                html.Td(student.get("status"))
                            ]),
                            html.Tr([html.Td("Average"),
                                     html.Td(average)])
                        ],
                                  borderless=True,
                                  hover=True,
                                  responsive=True,
                                  striped=True),
                    ]),
                    dbc.Col([
                        dbc.Table([
                            html.Tr([
                                html.Td(r.get("level")),
                                html.Td(r.get("name")),
                                html.Td(r.get("code")),
                                html.Td(r.get("total"))
                            ]) for r in results
                        ],
                                  bordered=True,
                                  hover=True,
                                  responsive=True,
                                  striped=True)
                    ])
                ])
            ],
            title=f'{student.get("given_name")} {student.get("family_name")}',
        )
        accordion_items.append(accordion_item)

    return "", accordion_items
