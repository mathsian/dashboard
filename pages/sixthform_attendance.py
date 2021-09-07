import dash_tabulator
import datetime
import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import curriculum
from app import app
import data
from dash_extensions.javascript import Namespace
ns = Namespace("myNameSpace", "tabulator")

layout = dbc.Row([
    dbc.Col([
        dbc.Button(children="Update", id={"type": "button", "section": "sixthform", "page": "attendance", "name": "update"}, color='primary')
    ],
align='end'
    ),
],
                 justify='end', align='end'
)
