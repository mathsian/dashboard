from dash import callback_context as cc
from flask import session
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
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace
import datetime

ns = Namespace("myNameSpace", "tabulator")

category_input = html.Div([
    dbc.Label("Category"),
    dcc.Dropdown(id={
        "type": "dropdown",
        "page": "student",
        "tab": "concern",
        "name": "category"
    },
                 options=curriculum.concern_categories_dropdown["options"],
                 value=curriculum.concern_categories_dropdown["default"],
                 clearable=False),
])

discrimination_input = html.Div([
    dbc.Label("Discrimination"),
    dcc.Dropdown(
        id={
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "discrimination"
        },
        options=curriculum.concern_discrimination_dropdown["options"],
        placeholder="Optional",
        multi=True,
    ),
    dbc.FormText("Select any that apply"),
])

description_input = html.Div([
    dbc.Label("Description"),
    dbc.Textarea(id={
        "type": "input",
        "page": "student",
        "tab": "concern",
        "name": "description"
    },
                 debounce=False,
                 placeholder="Description"),
])

stage_input = html.Div([
    dbc.Label("Stage"),
    dcc.Dropdown(id={
        "type": "dropdown",
        "page": "student",
        "tab": "concern",
        "name": "stage"
    },
                 options=curriculum.concern_stages_dropdown["options"],
                 value=curriculum.concern_stages_dropdown["default"],
                 clearable=False),
    dbc.FormText("For pastoral lead's use")
])

concern_message_input = html.Div([
    dbc.FormText(id={
        "type": "text",
        "page": "student",
        "tab": "concern",
        "name": "message"
    }),
])

concern_submit_input = html.Div([
    dbc.Button("Raise concern",
               id={
                   "type": "button",
                   "page": "student",
                   "tab": "concern",
                   "name": "submit"
               },
               color="secondary",
               n_clicks=0),
])

concern_form = dbc.Form([
    dbc.Row(children=[
        dbc.Col([
            category_input,
            description_input,
        ]),
        dbc.Col([
            discrimination_input,
            stage_input,
        ], width=2)
    ]),
    dbc.Row(children=[
        dbc.Col([
            concern_submit_input,
            concern_message_input,
        ], width=4),
    ])
])

layout = dbc.Container(concern_form)
@app.callback([
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "concern",
            "name": "message"
        }, "children"),
    Output(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
], [
    Input("sixthform-selected-store", "data"),
    Input(
        {
            "type": "input",
            "page": "student",
            "tab": "concern",
            "name": "description"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "category"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "stage"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "discrimination"
        }, "value"),
    Input(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
])
def update_concern_message(selected_student_ids, description, category, stage,
                           discrimination, n_clicks, button_color):
    if selected_student_ids:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(f'Raise {category} concern about')
        desc = html.Div(["For ", html.Blockquote(description)
                         ]) if description else html.Div()
        recipients = dbc.ListGroup(children=[
            dbc.ListGroupItem(f'{s.get("given_name")} {s.get("family_name")}')
            for s in enrolment_docs
        ])
        if cc.triggered and "n_clicks" in cc.triggered[0][
                "prop_id"] and button_color == "primary":
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            docs = [{
                "type": "concern",
                "student_id": s,
                "category": category,
                "stage": stage,
                "discrimination": discrimination,
                "description": description if description else "",
                "date": date,
                "from": session.get('email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Concern raised", "secondary"
        return [intro, recipients, desc], "primary"
    else:
        return "Select one or more students to raise concern", "secondary"
