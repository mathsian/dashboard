import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import urllib
from app import app
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

empty_layout = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "height": 320
            }
        } 
result_graph = dcc.Graph(id={
    "type": "graph",
    "section": "apprenticeships",
    "page": "academic",
    "tab": "view",
    "name": "bar"
},
                             config={
                                 "displayModeBar": False,
                                 "staticPlot": True,
                             },
                             figure={
                                 "layout": {
                                     "xaxis": {
                                         "visible": False
                                     },
                                     "yaxis": {
                                         "visible": False
                                     },
                                     "height": 320
                                 }
                             })

instance_info = [
    html.H4(id={"type": "text", "section": "apprenticeships", "page": "academic", "tab": "view", "name": "header"}),
]
layout = dbc.Container([
    dbc.Row([dbc.Col(instance_info)]),
            dbc.Row([dbc.Col([result_graph])]),
        ])


@app.callback(
    [
        Output(
        {
            "type": "graph",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "view",
            "name": "bar",
        }, "figure"),
        Output(
        {"type": "text", "section": "apprenticeships", "page": "academic", "tab": "view", "name": "header"}, "children"),
        ],
    [
        Input("apprenticeships-academic-store", "data"),
    ])
def update_subject_graph(store_data):
    instance_code = store_data.get("instance_code", False)
    if not instance_code:
        return empty_layout, "There are no results in this instance yet"
    # we added the class field before storing
    results_dicts = app_data.get_results_for_instance(instance_code)
    if not results_dicts:
        return empty_layout, "There are no results in this instance yet"
    results_df = pd.DataFrame.from_records(results_dicts)
    fig = app_data.graph_grade_profile(results_df)
    instance_dict = app_data.get_instance_by_instance_code(instance_code)
    header = f'{instance_dict.get("name")} - {instance_code} - {instance_dict.get("start_date")}'
    return fig, header
