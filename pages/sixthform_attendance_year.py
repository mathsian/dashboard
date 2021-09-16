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

gauge_last = daq.Gauge(
    id={
        "type": "gauge",
        "page": "summary",
        "tab": "attendance",
        "name": "last"
    },
    label="This month",
    labelPosition="bottom",
    size=200,
    scale={
        "start": 0,
        "interval": 5,
        "labelInterval": 2,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
)
gauge_cumulative = daq.Gauge(
    id={
        "type": "gauge",
        "page": "summary",
        "tab": "attendance",
        "name": "cumulative"
    },
    label="Overall",
    labelPosition="bottom",
    size=200,
    scale={
        "start": 0,
        "interval": 5,
        "labelInterval": 2,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
)
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
    value=92,
    marks={
        60: '60',
        80: '80',
        90: '90',
        92: '92',
        95: '95',
    },
)
layout = [
    dcc.Interval(id={
        "type": "interval",
        "page": "summary",
        "tab": "attendance"
    },
                 interval=60_000,
                 n_intervals=0),
    dbc.Row([
        dbc.Col(gauge_last),
        dbc.Col(gauge_cumulative, style={"float": "left"})
    ],
            align='center',
            justify='center'),
    dbc.Row(dbc.Col([graph_monthly, graph_threshold, threshold_slider]),
            align='start',
            justify='center')
]

callbacks = []


@app.callback([
    Output(
        {
            "type": "gauge",
            "page": "summary",
            "tab": "attendance",
            "name": "cumulative"
        }, "value"),
    Output(
        {
            "type": "gauge",
            "page": "summary",
            "tab": "attendance",
            "name": "last"
        }, "value"),
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
    Input({
        "type": "button",
        "section": "sixthform",
        "page": "attendance",
        "name": "update"
    }, "n_clicks"),
    Input(
        {
            "type": "slider",
            "page": "summary",
            "tab": "attendance",
            "name": "threshold",
        }, "value")
])
def update_attendance_dashboard(n_clicks, threshold):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(abspath('.')))
    sql_template = sql_jinja_env.get_template(
        'sql/cumulative attendance monthly.sql')
    sql = sql_template.render()
    rems_df = pd.read_sql(sql, conn)
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
    overall = rems_df.query(
        'student_id == "All" & date == "Year"')["attendance"].iat[0]
    last = rems_df.query('date != "Year"').query(
        'student_id == "All" & date == date.max()')["attendance"].iat[0]
    return overall, last, monthly_figure, low_figure