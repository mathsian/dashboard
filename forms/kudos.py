"""
Kudos report form
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
    html.Div(id="div-kudos-message"),
            dcc.Dropdown(
                id="dropdown-kudos-value",
                options=curriculum.values_dropdown["options"],
                value=curriculum.values_dropdown["default"],
            ),
            dcc.Dropdown(
                id="dropdown-kudos-points",
                options=curriculum.kudos_points_dropdown["options"],
                value=curriculum.kudos_points_dropdown["default"],
            ),
            dbc.Input(id="input-kudos-description", type="text", debounce=True, placeholder="Comment (optional)"),
            dbc.Button("Submit", id="kudos-submit-button", n_clicks=0),
            dcc.ConfirmDialog(id="dialog-kudos-confirm"),
        ]


def register_callbacks(app):
    @app.callback(
        [
            Output("dialog-kudos-confirm", "message"),
            Output("dialog-kudos-confirm", "displayed"),
        ],
        [Input("input-kudos-description", "n_submit"),
         Input("kudos-submit-button", "n_clicks")],
        [
            State("input-kudos-description", "value"),
            State("dropdown-kudos-value", "value"),
            State("dropdown-kudos-points", "value"),
            State("store-student", "data"),
        ],
    )
    def confirm_kudos(n_submit, n_clicks, description, value, points, store_student):
        if store_student:
            if n_submit or n_clicks:
                given_name = store_student.get("given_name")
                msg = f"Award {points} {value} kudos to {given_name}" 
                return msg, True
            else:
                return "Cancelled", False
        else:
            return "No student selected", False

    @app.callback(
        Output("div-kudos-message", "children"),
        [
            Input("dialog-kudos-confirm", "submit_n_clicks"),
            Input("store-student", "data"),
        ],
        [
            State("input-kudos-description", "value"),
            State("dropdown-kudos-value", "value"),
            State("dropdown-kudos-points", "value"),
        ],
    )
    def submit_kudos(clicks, store_student, description, value, points):
        if callback_context.triggered[0]['prop_id'] == "dialog-kudos-confirm.submit_n_clicks" and store_student:
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            doc = {
                "type": "kudos",
                "student_id": store_student["_id"],
                "ada_value": value,
                "points": points,
                "description": description,
                "date": date,
                "from": session.get('email',"none"),
            }
            data.save_docs([doc])
            return f"Kudos submitted to {store_student.get('given_name')}"
        elif store_student:
            return f"Award kudos to {store_student.get('given_name')}"
        else:
            return "Select student to award kudos"
