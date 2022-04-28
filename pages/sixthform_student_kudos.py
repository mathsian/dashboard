from flask import request
from flask_mailman import EmailMessage
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
import app_data
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
        "section": "sixthform",
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
        "section": "sixthform",
        "type": "dropdown",
        "page": "student",
        "tab": "kudos",
        "name": "points"
    },
               options=curriculum.kudos_points_dropdown["options"],
               value=curriculum.kudos_points_dropdown["default"])
])

kudos_notify_checkbox = html.Div([
    dbc.Label("Notify student(s) by email"),
    dbc.Checkbox(id={
        "section": "sixthform",
        "type": "checkbox",
        "page": "student",
        "tab": "kudos",
        "name": "notify"
    },
                 persistence=True)
])

kudos_description_input = html.Div([
    dbc.Label("Description"),
    dbc.Textarea(id={
        "section": "sixthform",
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
        "section": "sixthform",
        "type": "text",
        "page": "student",
        "tab": "kudos",
        "name": "message"
    })
])

kudos_submit_input = html.Div([
    dbc.Button("Award kudos",
               id={
        "section": "sixthform",
                   "type": "button",
                   "page": "student",
                   "tab": "kudos",
                   "name": "submit"
               },
               color="secondary",
               n_clicks=0),
])

kudos_form = dbc.Row(children=[
    dbc.Col([value_input, html.Br(), kudos_description_input, html.Br(), kudos_submit_input, html.Br(), kudos_message_input]),
    dbc.Col([points_input, html.Br(), kudos_notify_checkbox], width=4)
])

layout = dbc.Container(kudos_form)


@app.callback([
    Output(
        {
        "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "kudos",
            "name": "message"
        }, "children"),
    Output(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
    Output(
    {
        "section": "sixthform",
        "page": "student",
        "tab": "kudos",
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
            "tab": "kudos",
            "name": "description"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "value"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "points"
        }, "value"),
    Input(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
    State(
    {
        "section": "sixthform",
        "type": "checkbox",
        "page": "student",
        "tab": "kudos",
        "name": "notify"
    }, "value"),
])
def update_kudos_message(selected_student_ids, description, ada_value, points,
                         n_clicks, button_color, notify):
    # We need the number of outputs so we can set disabled on all but the first two
    editable = app_data.get_permissions(request.headers.get("X-Email")).get("can_edit_sf")
    # Pattern matched outputs is a sublist of cc.outputs
    pattern_matched_outputs = cc.outputs_list[2]
    disabled_outputs = [not editable for o in pattern_matched_outputs]
    if selected_student_ids and editable:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(
            f'Award {points} {ada_value} kudos from {request.headers.get("X-Email")} to')
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
                "from": request.headers.get('X-Email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            if notify:
                send_kudos_emails(enrolment_docs, ada_value, int(points), description if description else "", request.headers.get('X-Email', "none"))
            return "Kudos awarded", "secondary", disabled_outputs
        return [intro, recipients, desc], "primary", disabled_outputs
    elif editable:
        return "Select one or more students to award kudos", "secondary", disabled_outputs
    else:
        return "Only Sixth Form staff can award kudos to these students", "secondary", disabled_outputs


def send_kudos_emails(docs, ada_value, points, description, from_email):
    emails = [doc.get('student_email') for doc in docs]
    body = f'''
        Well done!

        You've been awarded {points} kudos for {ada_value} from {from_email}.
        '''
    if description:
        body += f'''
        They said,
        "{description}"
        '''
    message = EmailMessage(subject='Kudos!', body=body, bcc=emails)
    message.send(fail_silently=True)
