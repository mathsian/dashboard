import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from app import app
import data

tabs = ["Attendance"]
content = [
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=t, tab_id=f"summary-tab-{t.lower()}")
                    for t in tabs
                ],
                id=f"summary-tabs",
                card=True,
                active_tab=f"summary-tab-{tabs[0].lower()}",
            )),
        dbc.CardBody(id="summary-content", ),
    ]),
    dcc.Interval(id={
        "type": "interval",
        "page": "summary",
        "tab": "attendance"
    },
                 interval=60_000,
                 n_intervals=0),
]
attendance_dashboard = dbc.Container(children=[
    dbc.Row([
        dbc.Col(
            daq.Gauge(
                id={
                    "type": "gauge",
                    "page": "summary",
                    "tab": "attendance",
                    "name": "last"
                },
                label="This week",
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
            )),
        dbc.Col(
            daq.Gauge(
                id={
                    "type": "gauge",
                    "page": "summary",
                    "tab": "attendance",
                    "name": "cumulative"
                },
                label="Overall",
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
            ), )
    ]),
    dbc.Row([
        dcc.Graph(id={
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
                  config={"displayModeBar": False}),
        dcc.Graph(id={
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
                  config={"displayModeBar": False}),
    ]),
    html.Div([
        dcc.Slider(
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
        ),
    ]),
    html.Div(
        id={
            "type": "text",
            "page": "summary",
            "tab": "attendance",
            "name": "low_cumulative"
        }),
])

validation_layout = content + [attendance_dashboard]
tab_map = {"summary-tab-attendance": [attendance_dashboard]}


@app.callback([
    Output(f"summary-content", "children"),
], [Input(f"summary-tabs", "active_tab")])
def get_content(active_tab):
    return tab_map.get(active_tab)


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
    Output(
        {
            "type": "text",
            "page": "summary",
            "tab": "attendance",
            "name": "low_cumulative"
        }, "children")
], [
    Input({
        "type": "interval",
        "page": "summary",
        "tab": "attendance"
    }, "n_intervals"),
    Input(
        {
            "type": "slider",
            "page": "summary",
            "tab": "attendance",
            "name": "threshold",
        }, "value")
])
def update_attendance_gauge(n_intervals, threshold):
    # All weekly attendance records
    weekly_df = pd.DataFrame.from_records(
        data.get_data("all", "type_subtype", ["attendance", "weekly"]),
        columns=["date", "student_id", "actual", "possible"])
    # All monthly attendance records
    monthly_df = pd.DataFrame.from_records(
        data.get_data("all", "type_subtype", ["attendance", "monthly"]),
        columns=["date", "student_id", "actual", "possible"])
    # For overall cumulative attendance
    overall_sum = monthly_df.sum()
    overall = round(100 * overall_sum['actual'] / overall_sum['possible'], 1)
    # For this week
    last_sum = weekly_df.query("date == date.max()").sum()
    last = round(100 * last_sum['actual'] / last_sum['possible'], 1)
    # For proportion of sts with cumulative low attendance
    grouped_df = monthly_df.groupby("student_id").sum()
    grouped_df.eval("percent = 100 * actual / possible", inplace=True)
    low_cumulative = round(
        100 * len(grouped_df.query("percent < @threshold")) / len(grouped_df),
        1)
    low_cumulative_text = f"{low_cumulative}% of students have < {threshold}% overall attendance"
    # For monthly graph
    monthly_df.eval("percent = 100 * actual / possible", inplace=True)
    monthly_df["low"] = np.where(monthly_df["percent"] < threshold, 1, 0)
    monthly = monthly_df.groupby("date").agg({
        "percent": 'mean',
        "student_id": 'count',
        "low": 'sum',
    })
    monthly.eval("low_percent = 100 * low / student_id", inplace=True)
    monthly = monthly.round({'percent': 1, 'low_percent': 1})
    monthly.reset_index(inplace=True)
    monthly_figure = go.Figure(
        data=[
            go.Bar(
                x=monthly['date'],
                y=monthly['percent'],
                text=monthly['percent'],
                textposition='auto',
            ),
        ],
        layout={
            "title": "Monthly average student attendance",
            "yaxis": {
                "range": [60, 100]
            }
        },
    )
    low_figure = go.Figure(
        data=[
            go.Bar(
                x=monthly['date'],
                y=monthly['low_percent'],
                text=monthly['low_percent'],
                textposition='auto',
            ),
        ],
        layout={
            "title": f"Proportion of students with < {threshold}% attendance"
        },
    )
    return overall, last, monthly_figure, low_figure, low_cumulative_text
