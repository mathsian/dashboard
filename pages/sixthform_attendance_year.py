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
            "page": "summary",
            "tab": "attendance",
            "name": "monthly"
        }, "figure"),
    Output(
        {
            "type": "graph",
            "page": "summary",
            "tab": "attendance",
            "name": "low"
        }, "figure"),
], [
   Input(
        {
            "type": "slider",
            "page": "summary",
            "tab": "attendance",
            "name": "threshold",
        }, "value"),
    Input("sixthform-attendance-store", 'data')
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
            go.Bar(x=monthly_df['date'],
                   y=monthly_df['attendance'],
                   text=monthly_df['attendance'],
                   textposition='auto',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=monthly_df['date'],
                       y=monthly_df['cumulative'],
                       text=monthly_df['cumulative'],
                       textposition='top center',
                       marker_color='gold',
                       name="Cumulative"),
        ],
        layout={
            "title": "Monthly average student attendance",
            "yaxis": {
                "range": [60, 100]
            },
            "xaxis": {
                "tickmode": "array",
                "tickvals": months,
                # "ticktext": months
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
            go.Bar(x=low_grouped['date'],
                   y=low_grouped['percent'],
                   text=low_grouped['percent'],
                   textposition='auto',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=low_grouped['date'],
                       y=low_grouped['percentc'],
                       text=low_grouped['percentc'],
                       textposition='top center',
                       marker_color='gold',
                       name="Cumulative")
        ],
        layout={
            "xaxis": {
                "tickmode": "array",
                "tickvals": months,
                # "ticktext": months
            },
            "title": f"Proportion of students with < {threshold}% attendance"
        },
    )
    return monthly_figure, low_figure