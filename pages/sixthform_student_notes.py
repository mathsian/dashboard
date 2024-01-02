from dash import callback_context as cc
from flask import request
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from app import app
import data
import app_data
import curriculum
from dash_extensions.javascript import Namespace
import datetime
from datetime import date

ns = Namespace("myNameSpace", "tabulator")

category_input = html.Div([
    dbc.Label("Category"),
    dcc.Dropdown(id={
        "section": "sixthform",
        "type": "dropdown",
        "page": "student",
        "tab": "notes",
        "name": "category"
    },
        options=['Absence', 'Lateness'],
        value='Absence',
        clearable=False),
])

comment_date = html.Div([
    dbc.Label("Date"),
    html.Br(),
    dcc.DatePickerSingle(
        id={
            "type": "picker",
            "section": "sixthform",
            "page": "student",
            "tab": "notes",
            "name": "date"
        },
        date=date.today(),
        display_format="MMM DD YY",
    )
])

comment_checkbox = html.Div([
    dbc.Label('Include on report'),
    dbc.Checkbox(id={
        "type": "checkbox",
        "section": "sixthform",
        "page": "student",
        "tab": "notes",
        "name": "report"
    },
        value=True)
])

comment_input = html.Div([
    dbc.Label("Comment"),
    dbc.Textarea(id={
        "section": "sixthform",
        "type": "input",
        "page": "student",
        "tab": "notes",
        "name": "comment"
    },
        debounce=False,
        placeholder="Comment"),
])

comment_message = html.Div([
    dbc.FormText(id={
        "section": "sixthform",
        "type": "text",
        "page": "student",
        "tab": "notes",
        "name": "message"
    }),
])

comment_submit_button = html.Div([
    dbc.Button("Save note",
               id={
                   "section": "sixthform",
                   "type": "button",
                   "page": "student",
                   "tab": "notes",
                   "name": "submit"
               },
               color="secondary",
               n_clicks=0),
])

comment_form = dbc.Form([
    dbc.Row(children=[
        dbc.Col([category_input]),
        dbc.Col([comment_date]),
    ]),
    dbc.Row([
        dbc.Col([comment_input]),
        dbc.Col([comment_checkbox]),
    ]),
    dbc.Row(children=[
        dbc.Col([comment_message]),
        dbc.Col([
            comment_submit_button,
        ], width=2),
    ])
])

layout = dbc.Container(comment_form)


@app.callback([
    Output(
        {
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "notes",
            "name": "message"
        }, "children"),
    Output(
        {
            "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "notes",
            "name": "submit"
        }, "color"),
    Output(
        {
            "section": "sixthform",
            "page": "student",
            "tab": "notes",
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
            "tab": "notes",
            "name": "comment"
        }, "value"),
    Input(
        {
            "section": "sixthform",
            "type": "dropdown",
            "page": "student",
            "tab": "notes",
            "name": "category"
        }, "value"),
    Input(
        {
            "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "notes",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
            "section": "sixthform",
            "type": "button",
            "page": "student",
            "tab": "notes",
            "name": "submit"
        }, "color"),
    State(
        {
            "section": "sixthform",
            "type": "picker",
            "page": "student",
            "tab": "notes",
            "name": "date"
        }, "date"),
    State(
        {
            "section": "sixthform",
            "type": "checkbox",
            "page": "student",
            "tab": "notes",
            "name": "report"
        }, "value")
])
def update_concern_message(selected_student_ids, comment, category, n_clicks, button_color, date_value, report_value):
    # We need the number of outputs so we can set disabled on all but the first two
    editable = app_data.get_permissions(request.headers.get("X-Email")).get("sf_pastoral")
    # Pattern matched outputs is a sublist of cc.outputs
    pattern_matched_outputs = cc.outputs_list[2]
    disabled_outputs = [not editable for o in pattern_matched_outputs]

    if selected_student_ids and editable:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(f'Make {category} note about')
        recipients = dbc.ListGroup(children=[
            dbc.ListGroupItem(f'{s.get("given_name")} {s.get("family_name")}', color="primary")
            for s in enrolment_docs
        ])
        desc = html.Div([html.Blockquote(comment)]) if comment else html.Div()
        if cc.triggered and "n_clicks" in cc.triggered[0]["prop_id"] and button_color == "primary":
            docs = [{
                "type": "note",
                "student_id": s,
                "category": category,
                "comment": comment if comment else "",
                "date": date_value,
                "report": int(report_value),
                "date logged": date.today().strftime("%Y-%m-%d"),
                "from": request.headers.get('X-Email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Note saved", "secondary", disabled_outputs
        return [intro, recipients, desc], "primary", disabled_outputs
    elif editable:
        return "Select one or more students to make an attendance note", "secondary", disabled_outputs
    else:
        return "Only the Sixth Form pastoral team can make attendance notes for these students", "secondary", disabled_outputs
