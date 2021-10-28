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
import data
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
# assessment_colour_dropdown = dcc.Dropdown(id={
#     "page": "academic",
#     "tab": "view",
#     "type": "dropdown",
#     "name": "colour"
# },
#                                           options=[
#                                               {
#                                                   "label": "Maths",
#                                                   "value": "gc-ma"
#                                               },
#                                               {
#                                                   "label": "English",
#                                                   "value": "gc-en"
#                                               },
#                                               {
#                                                   "label": "Comp Sci",
#                                                   "value": "gc-comp.sci"
#                                               },
#                                           ],
#                                           value="gc-ma")

layout = dbc.Container([
            dbc.Row([dbc.Col([result_graph])]),
        ])


@app.callback(
    Output(
        {
            "type": "graph",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "view",
            "name": "bar",
        }, "figure"),
    [
        Input("apprenticeships-academic-store", "data"),
    ] )
def update_subject_graph(store_data):
    module_name = store_data.get("module")
    if not module_name:
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
    result_df = pd.DataFrame.from_records(store_data.get("result_docs"), columns=data.APPRENTICE_SCHEMA+data.RESULT_SCHEMA+["class"])
    bar_trace = go.Histogram(
        x=result_df["class"],
        hovertemplate="%{y:.0f}% %{x}<extra></extra>",
        histfunc='count',
        histnorm='percent'
    )
    fig = go.Figure()
    fig.update_xaxes(
        categoryorder='array',
        categoryarray=["Missing", "Fail", "Pass", "Merit", "Distinction"],
    )
    fig.add_trace(bar_trace)
    return fig
