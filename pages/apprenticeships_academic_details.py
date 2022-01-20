from flask import session
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import callback_context as cc
import pandas as pd
from app import app
import app_data


layout = dbc.Form(
    id={"type": "form", "section": "apprenticeships", "page": "academic", "tab": "details"}
)
@app.callback(
    Output(
        {"type": "form", "section": "apprenticeships", "page": "academic", "tab": "details"}, "children"),
    [
    Input("apprenticeships-academic-store", "data")
])
def update_instance_form(store_data):
    instance_code = store_data.get("instance_code")
    if not instance_code:
        return []
    permissions = app_data.get_permissions(session.get('email'))
    components = app_data.get_components_by_instance_code(instance_code)
    instance = app_data.get_instance_by_instance_code(instance_code)
    header = html.Div([
        html.H4(f'{instance.get("module_name")} - {instance_code}'),
    ])
    first_teaching = dbc.Row([
        dbc.Col([
            dbc.Label("First teaching", html_for="fwb"),
            dbc.Input(id="fwb", value=instance.get("start_date"), disabled=True)
        ], width='3'),
        dbc.Col([
            dbc.Label("Second week", html_for="swb"),
            dbc.Input(id="swb", value=instance.get("second_date"), disabled=True)
        ], width='3'),
        dbc.Col([
            dbc.Label("Moderated", html_for="mod"),
            dbc.Checkbox(id="mod", value=instance.get("moderated"), disabled=not permissions.get("can_moderate_ap"))
        ], width='1')
        ])
    component_list = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label(f"Component {i + 1}", html_for=f'name_{c.get("component_id")}'),
                dbc.Input(id=f'name_{c.get("component_id")}', value=c.get("component_name"), disabled=True)
                ], width='3'),
            dbc.Col([
                dbc.Label("Weight", html_for=f'weight_{c.get("component_id")}'),
                dbc.Input(id=f'weight_{c.get("component_name")}', value=c.get("weight"), type='number', disabled=True)
            ], width='1')
            ]) for (i, c) in enumerate(components)])
    submit_button = html.Div([
        dbc.Button("Save",
               id={
                   "type": "button",
                   "section": "apprenticeships",
                   "page": "academic",
                   "tab": "details",
                   "name": "submit"
               },
               color="secondary",
               disabled=not permissions.get("can_moderate_ap"),
               n_clicks=0),
    ])

    return html.Div([header, first_teaching, component_list, submit_button])

@app.callback(
    Output(
{
                   "type": "button",
                   "section": "apprenticeships",
                   "page": "academic",
                   "tab": "details",
                   "name": "submit"
}, "color"
    ),
    [Input("mod", "value"),
     Input(
{
                   "type": "button",
                   "section": "apprenticeships",
                   "page": "academic",
                   "tab": "details",
                   "name": "submit"
}, "n_clicks"
     )],
[State(
{
                   "type": "button",
                   "section": "apprenticeships",
                   "page": "academic",
                   "tab": "details",
                   "name": "submit"
}, "color"
),
 State("apprenticeships-academic-store", "data")])
def submit_form(mod_value, n_clicks, submit_button_color, store_data):
    if cc.triggered and "n_clicks" in cc.triggered[0]["prop_id"] and submit_button_color == "primary":
        app_data.set_moderated_by_instance_code(store_data.get("instance_code"), mod_value)
        return "secondary"
    else:
        instance = app_data.get_instance_by_instance_code(store_data.get("instance_code"))
        if instance.get("moderated") != mod_value:
            return "primary"
        else:
            return "secondary"
 
