import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL
import pandas as pd

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
                label="Last week",
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
    ])
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
], [
    Input({
        "type": "interval",
        "page": "summary",
        "tab": "attendance"
    }, "n_intervals"),
])
def update_attendance_gauge(n_intervals):
    attendance_df = pd.DataFrame.from_records(
        data.get_data("all", "type", "attendance"),
        columns=["date", "actual", "possible"])
    overall_sum = attendance_df.sum()
    overall = round(100 * overall_sum['actual'] / overall_sum['possible'])
    last_sum = attendance_df.query("date == date.max()").sum()
    last = round(100 * last_sum['actual'] / last_sum['possible'])
    return overall, last
