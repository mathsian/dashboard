import filters
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
import urllib
from app import app
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

result_graph = dcc.Graph(id={
    "type": "graph",
    "section": "apprenticeships",
    "page": "academic",
    "tab": "view",
    "name": "bar"
},
                             config={
                                 "displayModeBar": False,
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
    ] )
def update_subject_graph(store_data):
    instance_code = store_data.get("instance_code", False)
    if not instance_code:
        return {
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
    # we added the class field before storing
    result_df = pd.DataFrame.from_records(app_data.get_results_for_instance(instance_code))
    labels=["Missing", "Fail", "Pass", "Merit", "Distinction", "Error"]
    result_df["class"] = pd.cut(result_df["total"], [-float("inf"), 0, 39.5, 59.5, 69.5, 101, float("inf")], labels=labels)
    bar_trace = go.Histogram(
        x=result_df["class"],
        hovertemplate="%{y:.0f}% %{x}<extra></extra>",
        histfunc='count',
        histnorm='percent'
    )
    fig = go.Figure()
    fig.update_xaxes(
        categoryorder='array',
        categoryarray=labels,
    )
    fig.add_trace(bar_trace)
    instance_dict = app_data.get_instance_by_instance_code(instance_code)
    header = f'{instance_dict.get("module_name")} - {instance_code} - {instance_dict.get("start_date")}'
    return fig, header
