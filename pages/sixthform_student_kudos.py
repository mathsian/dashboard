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
from flask import session
from dash import callback_context as cc
import datetime


#import tasks
from configparser import ConfigParser
from redmail import gmail
config_object = ConfigParser()
config_file = 'config.ini'
config_object.read(config_file)
mail_config = config_object['SMTP']

gmail.username = mail_config['username']
gmail.password = mail_config['password']

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
        persistence=True,
        persistence_type='memory'
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

kudos_toast = dbc.Toast(id={
                "section": "sixthform",
                "type": "toast",
                "page": "student",
                "tab": "kudos",
                "name": "notifications"
    },
              is_open=False,
              duration=5000)

kudos_form = dbc.Container([
    dbc.Row(children=[
        dbc.Col([value_input, html.Br(), kudos_description_input]),
        dbc.Col([points_input, html.Br(), kudos_notify_checkbox], width=4)
    ]),
    html.Br(),
    dbc.Row(children=[
        dbc.Col([kudos_message_input]),
        dbc.Col([kudos_submit_input], width=4),
    ])
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
    }, "disabled"),
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
],
)
def update_kudos_message(selected_student_ids, description, ada_value, points,
                         n_clicks, button_color, notify):
    # We need the number of outputs so we can set disabled on all but the first two
    user_email = request.headers.get("X-Email")
    editable = app_data.get_permissions(user_email).get("can_edit_sf")
    # Pattern matched outputs is a sublist of cc.outputs
    pattern_matched_outputs = cc.outputs_list[2]
    disabled_outputs = [not editable for o in pattern_matched_outputs]
    if selected_student_ids and editable:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(
            f'Award {points} {ada_value} kudos from {user_email} to')
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
                "type": "kudos",
                "student_id": s,
                "ada_value": ada_value,
                "points": int(points), # the values are ints already but somehow they end up a string
                "description": description if description else "",
                "date": date,
                "from": user_email,
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Kudos awarded", "secondary", disabled_outputs
        return [intro, recipients, desc], "primary", disabled_outputs
    elif editable:
        return "Select one or more students to award kudos", "secondary", disabled_outputs
    else:
        return "Only Sixth Form staff can award kudos to these students", "secondary", disabled_outputs

@app.callback(
[
    Output({
                "section": "sixthform",
                "type": "toast",
                "page": "student",
                "tab": "kudos",
                "name": "notifications"
    }, "is_open"),
    Output({
                "section": "sixthform",
                "type": "toast",
                "page": "student",
                "tab": "kudos",
                "name": "notifications"
    }, "children"),
],
[
    Input(
        {
        "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "n_clicks")
], [
   State("sixthform-selected-store", "data"),
    State(
        {
        "section": "sixthform",
            "type": "input",
            "page": "student",
            "tab": "kudos",
            "name": "description"
        }, "value"),
    State(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "value"
        }, "value"),
    State(
        {
        "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "points"
        }, "value"),
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
]
,
    prevent_initial_call=True)
def send_email(n_clicks, selected_student_ids, description, ada_value, points, button_color, notify):
    if not notify or not selected_student_ids or n_clicks < 1 or button_color != 'primary':
        raise PreventUpdate

    user_email = request.headers.get("X-Email")
    enrolment_docs = data.get_students(selected_student_ids)
    emails = [doc.get('student_email') for doc in enrolment_docs if doc.get('student_email', False)]
    body = f'''
        Well done!

        You've been awarded {int(points)} kudos {"point" if int(points) == 1  else "points"} for {ada_value} from {user_email}.
        '''
    if description:
        body += f'''
        They said,
        "{description}"
        '''
    try:
        app.logger.info(f"Sending email: kudos from {user_email} to {emails}")
        gmail.send(subject='Kudos!',
                bcc=emails,
                text=body
                )
        app.logger.info(f"Email sent: kudos from {user_email} to {emails}")
        return True, f"Email sent to {', '.join(emails)}"
    except Exception as e:
        app.logger.info(f"Email failed: kudos from {user_email} to {emails}")
        app.logger.info(f"{e}")
        return True, f"Email not sent. The problem has been logged"
