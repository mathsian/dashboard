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

layout = dbc.Row(dbc.Col(dbc.CardGroup(
        id={
            "section": "apprenticeships",
            "type": "card_group",
            "page": "student",
            "tab": "report",
            "name": "cards"
        }
)))


@app.callback([
    Output(
        {
            "section": "apprenticeships",
            "type": "card_group",
            "page": "student",
            "tab": "report",
            "name": "cards"
        }, "children"),
], [Input("apprenticeships-selected-store", "data")])
def update_student_report(store_data):
    if not store_data:
        return [html.H4("Select a student to view their report")]
    cards = []
    for student_id in store_data:
        student = app_data.get_student_by_id(student_id)
        results = app_data.get_results_for_student(student_id)
        if len(results):
            average = round(sum([r.get('total') for r in results])/len(results), 0)
        else:
            average = "-"
        card = dbc.Card(id={
            "type": "card", "section": "apprenticeships", "page": "student", "tab": "report", "name": f'{student_id}'
        }, children=[
            dbc.CardHeader(f'{student.get("given_name")} {student.get("family_name")}'),
            dbc.CardBody(html.Table([
                html.Tr([html.Td("Employer"), html.Td(student.get("employer"))]),
                html.Tr([html.Td("Status"), html.Td(student.get("status"))]),
                html.Tr([html.Td("Average"), html.Td(average)])
                ]))
        ],
        style={"min-width": "18rem", "max-width": "18rem"}
        )
        cards.append(card)
        cards.append(dbc.Popover(target={
            "type": "card", "section": "apprenticeships", "page": "student", "tab": "report", "name": f'{student_id}'
        }, children=html.Table([html.Tr([html.Td(r.get("instance_code")), html.Td(r.get("total"))]) for r in results]),
                                 placement='left',
                                 trigger='click'))
    return [cards]
