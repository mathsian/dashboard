from dash import callback_context as cc
from flask import request
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
import data
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace
import datetime

ns = Namespace("myNameSpace", "tabulator")

category_input = html.Div([
    dbc.Label("Category"),
    dcc.Dropdown(id={
        "section": "sixthform",
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
        "section": "sixthform",
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
        "section": "sixthform",
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
        "section": "sixthform",
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
        "section": "sixthform",
        "type": "text",
        "page": "student",
        "tab": "concern",
        "name": "message"
    }),
])

concern_submit_input = html.Div([
    dbc.Button("Raise concern",
               id={
        "section": "sixthform",
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
            html.Br(),
            description_input,
        ]),
        dbc.Col([
            discrimination_input,
            html.Br(),
            stage_input,
        ], width=2)
    ]),
    html.Br(),
    dbc.Row(children=[
        dbc.Col([
            concern_message_input
        ]),
        dbc.Col([
            concern_submit_input,
        ], width=2),
    ])
])

layout = dbc.Container(concern_form)
@app.callback([
    Output(
        {
        "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "concern",
            "name": "message"
        }, "children"),
    Output(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
    Output(
    {
        "section": "sixthform",
        "page": "student",
        "tab": "concern",
        "type": ALL,
        "name": ALL
    }, "disabled")
], [
    Input("sixthform-selected-store", "data"),
    Input(
        {
        "section": "sixthform",
            "type": "input",
            "page": "student",
            "tab": "concern",
            "name": "description"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "category"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "stage"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "discrimination"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
])
def update_concern_message(selected_student_ids, description, category, stage,
                           discrimination, n_clicks, button_color):
    # We need the number of outputs so we can set disabled on all but the first two
    editable = app_data.get_permissions(request.headers.get("X-Email")).get("can_edit_sf")
    # Pattern matched outputs is a sublist of cc.outputs
    pattern_matched_outputs = cc.outputs_list[2]
    disabled_outputs = [not editable for o in pattern_matched_outputs]
 
    if selected_student_ids and editable:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(f'Raise {category} concern about')
        desc = html.Div(["For ", html.Blockquote(description)
                         ]) if description else html.Div()
        recipients = dbc.ListGroup(children=[
            dbc.ListGroupItem(f'{s.get("given_name")} {s.get("family_name")}') if not s.get("notes for comments", False) else dbc.ListGroupItem([f'{s.get("given_name")} {s.get("family_name")}', html.Br(), f'{s.get("notes for comments")}'], color="primary")
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
                "from": request.headers.get('X-Email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Concern raised", "secondary", disabled_outputs
        return [intro, recipients, desc], "primary", disabled_outputs
    elif editable:
        return "Select one or more students to raise concern", "secondary", disabled_outputs
    else:
        return "Only Sixth Form staff can raise concerns for these students", "secondary", disabled_outputs
