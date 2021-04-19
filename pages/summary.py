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

tabs = ["Attendance", "Unauthorised", "Missing"]
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
    dbc.Row(
        [
            dbc.Col(daq.Gauge(
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
            ),
                    width=4),
            dbc.Col(daq.Gauge(
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
            ),
                    width=4)
        ],
        align='center',
        justify='center',
    ),
    dbc.Row(
        dbc.Col([
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
        ], ),
        align='start',
        justify='center',
    )
])
unauthorised_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "summary",
        "tab": "unauthorised",
    },
    options={
        "resizableColumns": False,
        "layout": "fitData"
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
        "title": "Date",
        "field": "date"
    }, {
        "title": "Given name",
        "field": "given_name",
        "headerFilter": True,
    }, {
        "headerFilter": True,
        "title": "Surname",
        "field": "family_name"
    }, {
        "headerFilter": True,
        "title": "Subject",
        "field": "subject_code"
    }, {
        "title": "Day",
        "field": "day"
    }, {
        "title": "Period",
        "field": "period"
    }])
missing_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "summary",
        "tab": "missing",
    },
    options={
        "resizableColumns": False,
        "layout": "fitData"
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
        "title": "Date",
        "field": "date"
    }, {
        "title": "Register",
        "field": "register"
    }, {
        "title": "Period",
        "field": "period"
    }, {
        "title": "Lecturer",
        "field": "lecturer"
    }])
validation_layout = content + [
    attendance_dashboard, unauthorised_table, missing_table
]
tab_map = {
    "summary-tab-attendance": [attendance_dashboard],
    "summary-tab-unauthorised":
    [dbc.Col([html.H3("Last 10 days"), unauthorised_table])],
    "summary-tab-missing":
    [dbc.Col([html.H3("Missing registers"), missing_table])]
}


@app.callback([
    Output(f"summary-content", "children"),
], [Input(f"summary-tabs", "active_tab")])
def get_content(active_tab):
    return tab_map.get(active_tab)


@app.callback(
    Output({
        "type": "table",
        "page": "summary",
        "tab": "missing",
    }, "data"), [
        Input({
            "type": "interval",
            "page": "summary",
            "tab": "attendance"
        }, "n_intervals")
    ])
def update_missing_table(n_intervals):
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
    sql_template = sql_jinja_env.get_template('sql/missing registers.sql')
    date_end = datetime.date.today()
    date_start = date_end - datetime.timedelta(days=10)
    template_vars = {
        "date_end": date_end.isoformat(),
        "date_start": date_start.isoformat(),
    }
    sql = sql_template.render(template_vars)
    df = pd.read_sql(sql, conn)
    return df.to_dict(orient='records')


@app.callback(
    Output({
        "type": "table",
        "page": "summary",
        "tab": "unauthorised",
    }, "data"), [
        Input({
            "type": "interval",
            "page": "summary",
            "tab": "attendance"
        }, "n_intervals")
    ])
def update_unauthorised_table(n_intervals):
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
    sql_template = sql_jinja_env.get_template('sql/unauthorised absences.sql')
    date_end = datetime.date.today()
    date_start = date_end - datetime.timedelta(days=10)
    template_vars = {
        "date_end": date_end.isoformat(),
        "date_start": date_start.isoformat(),
    }
    sql = sql_template.render(template_vars)
    df = pd.read_sql(sql, conn)
    return df.to_dict(orient='records')


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
        'sql/attendance by student monthly with subtotals.sql')
    sql = sql_template.render()
    rems_df = pd.read_sql(sql, conn)
    sql_template = sql_jinja_env.get_template(
        'sql/cumulative attendance monthly.sql')
    sql = sql_template.render()
    cumulative_df = pd.read_sql(sql, conn)
    low_cumulative_text = f"low_cumulative of students have < {threshold}% overall attendance"
    # For monthly graph
    monthly_df = rems_df.query('date != "Year" & student_id == "All"')
    monthly_figure = go.Figure(
        data=[
            go.Bar(x=monthly_df['date'],
                   y=monthly_df['attendance'],
                   text=monthly_df['attendance'],
                   textposition='auto',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=cumulative_df['date'],
                       y=cumulative_df['cumulative'],
                       text=cumulative_df['cumulative'],
                       textposition='top center',
                       marker_color='gold',
                       name="Cumulative"),
        ],
        layout={
            "title": "Monthly average student attendance",
            "yaxis": {
                "range": [60, 100]
            }
        },
    )
    # For low attendance graph
    low_df = rems_df.query("date != 'Year' and student_id != 'All'")
    low_df["low"] = (low_df["attendance"] < threshold).astype('int')
    low_grouped = low_df.groupby("date").agg({
        "low": ["count", "sum"]
    }).reset_index()
    low_grouped['percent'] = round(
        100 * low_grouped['low', 'sum'] / low_grouped['low', 'count'], 2)
    low_grouped['low',
                'cumcount'] = low_grouped['low',
                                          'count'].transform(pd.Series.cumsum)
    low_grouped['low',
                'cumsum'] = low_grouped['low',
                                        'sum'].transform(pd.Series.cumsum)
    low_grouped['cumulative'] = round(
        100 * low_grouped['low', 'cumsum'] / low_grouped['low', 'cumcount'], 2)
    low_figure = go.Figure(
        data=[
            go.Bar(x=low_grouped['date'],
                   y=low_grouped['percent'],
                   text=low_grouped['percent'],
                   textposition='auto',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=low_grouped['date'],
                       y=low_grouped['cumulative'],
                       text=low_grouped['cumulative'],
                       textposition='top center',
                       marker_color='gold',
                       name="Cumulative")
        ],
        layout={
            "title": f"Proportion of students with < {threshold}% attendance"
        },
    )
    overall = rems_df.query(
        'student_id == "All" & date == "Year"')["attendance"].iat[0]
    last = rems_df.query('date != "Year"').query(
        'student_id == "All" & date == date.max()')["attendance"].iat[0]
    return overall, last, monthly_figure, low_figure, low_cumulative_text
