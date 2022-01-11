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

graph_monthly = dcc.Graph(id={
    "type": "graph",
            "section": "apprenticeships",
    "page": "summary",
    "tab": "attendance",
    "name": "monthly"
},
                          figure={
                              "layout": {
                                  "xaxis": {
                                      "visible": False
                                  },
                                  "yaxis": {
                                      "visible": False
                                  }
                              }
                          },
                          config={"displayModeBar": False})
graph_threshold = dcc.Graph(id={
    "type": "graph",
            "section": "apprenticeships",
    "page": "summary",
    "tab": "attendance",
    "name": "low"
},
                            figure={
                                "layout": {
                                    "xaxis": {
                                        "visible": False
                                    },
                                    "yaxis": {
                                        "visible": False
                                    }
                                }
                            },
                            config={"displayModeBar": False})
threshold_slider = dcc.Slider(
    id={
        "type": "slider",
            "section": "apprenticeships",
        "page": "summary",
        "tab": "attendance",
        "name": "threshold",
    },
    min=0,
    max=100,
    value=90,
    marks={
        60: '60',
        80: '80',
        90: '90',
        92: '92',
        95: '95',
    },
)
layout = dbc.Row(dbc.Col([graph_monthly, graph_threshold, threshold_slider]), align='start', justify='center')



@app.callback([
   Output(
        {
            "type": "graph",
            "section": "apprenticeships",
            "page": "summary",
            "tab": "attendance",
            "name": "monthly"
        }, "figure"),
    Output(
        {
            "type": "graph",
            "section": "apprenticeships",
            "page": "summary",
            "tab": "attendance",
            "name": "low"
        }, "figure"),
], [
   Input(
        {
            "type": "slider",
            "section": "apprenticeships",
            "page": "summary",
            "tab": "attendance",
            "name": "threshold",
        }, "value"),
    Input("apprenticeships-attendance-store", 'data')
])
def update_attendance_dashboard(threshold, store_data):
    rems_df = pd.DataFrame.from_records(store_data)
    rems_df["low"] = (rems_df["attendance"] < threshold).astype('int')
    rems_df["lowc"] = (rems_df["cumulative"] < threshold).astype('int')
    # For monthly graph
    monthly_df = rems_df.query('date != "Year" & student_id == "All"')
    months = list(monthly_df['date'])
    monthly_figure = go.Figure(
        data=[
            go.Bar(x=monthly_df['date'].astype('datetime64'),
                   y=monthly_df['attendance'],
                   text=monthly_df['attendance'],
                   textposition='auto',
                   hovertemplate="During %{x}<br>%{y}",
                   xperiod='M1',
                   xperiodalignment='middle',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=monthly_df['date'].astype('datetime64'),
                       y=monthly_df['cumulative'],
                       text=monthly_df['cumulative'],
                       textposition='top center',
                       marker_color='gold',
                       name="Year to date",
                       hovertemplate="At end of %{x}<br>%{y}",
                       xperiod='M1',
                       xperiodalignment='end',
)
        ],
        layout={
            "title": "Monthly average learner attendance",
            "yaxis": {
                "range": [60, 100]
            },
            "xaxis": {
                "ticklabelmode": 'period',
                "tickformat": "%b %Y",
            }
       },
    )
    # For low attendance graph
    low_df = rems_df.query("date != 'Year' and student_id != 'All'")
    low_grouped = low_df.groupby("date").agg({
        "low": ["count", "sum"],
        "lowc": ["count", "sum"]
    }).reset_index()
    low_grouped['percent'] = round(
        100 * low_grouped['low', 'sum'] / low_grouped['low', 'count'], 1)
    low_grouped['percentc'] = round(
        100 * low_grouped['lowc', 'sum'] / low_grouped['lowc', 'count'], 1)
    low_figure = go.Figure(
        data=[
            go.Bar(x=low_grouped['date'].astype('datetime64'),
                   y=low_grouped['percent'],
                   text=low_grouped['percent'],
                   textposition='auto',
                   marker_color='steelblue',
                   hovertemplate="During %{x}<br>%{y}",
                   xperiod='M1',
                   xperiodalignment='middle',
                   name="Monthly"),
            go.Scatter(x=low_grouped['date'].astype('datetime64'),
                       y=low_grouped['percentc'],
                       text=low_grouped['percentc'],
                       textposition='top center',
                       marker_color='gold',
                       xperiod='M1',
                       hovertemplate="At end of %{x}<br>%{y}",
                       xperiodalignment='end',
                       name="Year to date")
        ],
        layout={
            "xaxis": {
                "ticklabelmode": 'period',
                "tickformat": "%b %Y",
            },
           "title": f"Proportion of learners with < {threshold}% attendance"
        },
    )
    return monthly_figure, low_figure
