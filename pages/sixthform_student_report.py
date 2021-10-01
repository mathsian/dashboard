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
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

layout = html.Div(id={"type": "text",
                      "section": "sixthform",
                      "page": "student",
                      "tab": "report",
                      "name": "report_div"})


@app.callback(
    Output(
{"type": "text",
                      "section": "sixthform",
                      "page": "student",
                      "tab": "report",
                      "name": "report_div"}
        ,"children"),
    [Input("sixthform-selected-store", "data")]
    )
def update_report(store_data):
    return store_data
