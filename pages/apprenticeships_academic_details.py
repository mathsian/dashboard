import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
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
    instance = store_data.get("instance")
    if not instance:
        return []
    components = app_data.get_components_by_instance_code(instance.get("instance_code"))
    header = html.Div([
        html.H4(f'{instance.get("module_name")} - {instance.get("instance_code")}'),
    ])
    first_teaching = dbc.Row([
        dbc.Col([
            dbc.Label("First teaching", html_for="fwb"),
            dbc.Input(id="fwb", value=instance.get("start_date"))
        ], width='3'),
        dbc.Col([
            dbc.Label("Second week", html_for="swb"),
            dbc.Input(id="swb", value=instance.get("second_date"))
        ], width='3'),
        dbc.Col([
            dbc.Label("Moderated", html_for="mod"),
            dbc.Checkbox(id="mod", value=instance.get("moderated"))
        ], width='1')
        ])
    component_list = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label(f"Component {i + 1}", html_for=f'name_{c.get("component_id")}'),
                dbc.Input(id=f'name_{c.get("component_id")}', value=c.get("component_name"))
                ], width='3'),
            dbc.Col([
                dbc.Label("Weight", html_for=f'weight_{c.get("component_id")}'),
                dbc.Input(id=f'weight_{c.get("component_name")}', value=c.get("weight"), type='number')
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
               n_clicks=0),
    ])

    return html.Div([header, first_teaching, component_list, submit_button])
