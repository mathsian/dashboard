import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import app_data
import dash_bootstrap_components as dbc

layout = dbc.Row(
    dbc.Col(
        dbc.Accordion(
            id={
                "section": "apprenticeships",
                "type": "accordion",
                "page": "employers",
                "tab": "report",
                "name": "reports"
            })))


@app.callback([
    Output(
        {
            "section": "apprenticeships",
            "type": "accordion",
            "page": "employers",
            "tab": "report",
            "name": "reports"
        }, "children"),
], [
    Input(
        {
            "section": "apprenticeships",
            "type": "storage",
            "page": "employers",
            "name": "selected"
        }, "data")
])
def update_student_report(store_data):
    if not store_data:
        return [dbc.AccordionItem(title="Select students to view their reports")]
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
                "page": "employers",
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
    return [accordion_items]
