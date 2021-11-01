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
from flask import session
from dash import callback_context as cc
import datetime

ns = Namespace("myNameSpace", "tabulator")
value_input = html.Div([
    dbc.Label("Value"),
    dbc.Select(
        id={
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "value"
        },
        options=curriculum.values_dropdown["options"],
        value=curriculum.values_dropdown["default"],
    )
])

points_input = html.Div([
    dbc.Label("Points"),
    dbc.Select(id={
        "type": "dropdown",
        "page": "student",
        "tab": "kudos",
        "name": "points"
    },
               options=curriculum.kudos_points_dropdown["options"],
               value=curriculum.kudos_points_dropdown["default"])
])

kudos_description_input = html.Div([
    dbc.Label("Description"),
    dbc.Textarea(id={
        "type": "input",
        "page": "student",
        "tab": "kudos",
        "name": "description"
    },
                 debounce=False,
                 placeholder="Description"),
])

kudos_message_input = html.Div([
    dbc.FormText(id={
        "type": "text",
        "page": "student",
        "tab": "kudos",
        "name": "message"
    })
])

kudos_submit_input = html.Div([
    dbc.Button("Award kudos",
               id={
                   "type": "button",
                   "page": "student",
                   "tab": "kudos",
                   "name": "submit"
               },
               color="secondary",
               n_clicks=0),
])

kudos_form = dbc.Row(children=[
    dbc.Col([value_input, kudos_description_input, kudos_submit_input, kudos_message_input]),
    dbc.Col([points_input], width=4)
])

layout = dbc.Container(kudos_form)


@app.callback([
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "kudos",
            "name": "message"
        }, "children"),
    Output(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
], [
    Input("sixthform-selected-store", "data"),
    Input(
        {
            "type": "input",
            "page": "student",
            "tab": "kudos",
            "name": "description"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "value"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "points"
        }, "value"),
    Input(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
])
def update_kudos_message(selected_student_ids, description, ada_value, points,
                         n_clicks, button_color):
    if selected_student_ids:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(
            f'Award {points} {ada_value} kudos from {session.get("email")} to')
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
                "type": "kudos",
                "student_id": s,
                "ada_value": ada_value,
                "points": int(points), # the values are ints already but somehow they end up a string
                "description": description if description else "",
                "date": date,
                "from": session.get('email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Kudos awarded", "secondary"
        return [intro, recipients, desc], "primary"
    else:
        return "Select one or more students to award kudos", "secondary"

