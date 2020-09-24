"""
Conern report form
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import curriculum
from dash import callback_context
from dash.dependencies import Input, Output, State
import datetime
import data
from flask import session

layout = [
    html.Div(id="div-concern-message"),
            dcc.Dropdown(
                id="dropdown-concern-category",
                options=curriculum.concern_categories_dropdown["options"],
                value=curriculum.concern_categories_dropdown["default"],
            ),
            dbc.Input(id="input-concern-description", type="text", debounce=True, placeholder="Description"),
            dcc.Dropdown(
                id="dropdown-concern-discrimination",
                options=curriculum.concern_discrimination_dropdown["options"],
                placeholder="Discrimination (optional)",
                multi=True,
                ),
            dbc.Button("Submit", id="concern-submit-button", n_clicks=0),
            dcc.ConfirmDialog(id="dialog-concern-confirm"),
        ]

def register_callbacks(app):
    @app.callback(
        [
            Output("dialog-concern-confirm", "message"),
            Output("dialog-concern-confirm", "displayed"),
        ],
        [Input("input-concern-description", "n_submit"),
         Input("concern-submit-button", "n_clicks")],
        [
            State("input-concern-description", "value"),
            State("dropdown-concern-category", "value"),
            State("dropdown-concern-discrimination", "value"),
            State("store-student", "data"),
        ],
    )
    def confirm_concern(n_submit, n_clicks, description, category, discrimination, store_student):
        if store_student:
            if n_submit or n_clicks:
                given_name = store_student.get("given_name")
                msg = f"Raise {value} concern for {given_name}?" 
                return msg, True
            else:
                return "Cancelled", False
        else:
            return "No student selected", False

    @app.callback(
        Output("div-concern-message", "children"),
        [
            Input("dialog-concern-confirm", "submit_n_clicks"),
            Input("store-student", "data"),
        ],
        [
            State("input-concern-description", "value"),
            State("dropdown-concern-category", "value"),
            State("dropdown-concern-discrimination", "value"),
        ],
    )
    def submit_concern(clicks, store_student, description, category, discrimination):
        if callback_context.triggered[0]['prop_id'] == "dialog-concern-confirm.submit_n_clicks" and store_student:
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            doc = {
                "type": "concern",
                "student_id": store_student["_id"],
                "category": category,
                "discrimination": discrimination,
                "description": description,
                "date": date,
                "from": session.get('email', "none"),
            }
            data.save_docs([doc])
            return f"Concern submitted to {store_student.get('given_name')}"
        elif store_student:
            return f"Raise concern about {store_student.get('given_name')}"
        else:
            return "Select student to raise concern"
