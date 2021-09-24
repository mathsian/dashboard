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

tabs = ["Attendance", "Unauthorised", "Missing", "Progress"]
content = [
    dbc.Card([
        dbc.CardHeader(dbc.Tabs(
            [
                dbc.Tab(label=t, tab_id=f"summary-tab-{t.lower()}")
                for t in tabs
            ],
            id=f"summary-tabs",
            card=True,
            active_tab=f"summary-tab-{tabs[0].lower()}",
        ),
),
        dbc.CardBody(id="summary-content"),
    ]),
    dcc.Interval(id={
        "type": "interval",
        "page": "summary",
        "tab": "attendance"
    },
                 interval=600_000,
                 n_intervals=0),
]
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
attendance_dashboard = [
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
unauthorised_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "summary",
        "tab": "unauthorised",
    },
    options={
        "resizableColumns": False,
        "layout": "fitData",
        "groupBy": "date",
        "maxHeight": "60vh",
        "groupHeader": ns("groupHeader"),
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
        "title": "Date",
        "field": "date",
        "visible": False,
    }, {
        "title": "Given name",
        "field": "given_name",
        "headerFilter": True,
        "widthGrow": 3,
    }, {
        "headerFilter": True,
        "title": "Surname",
        "field": "family_name",
        "widthGrow": 3,
    }, {
        "title": "Marks",
        "field": "marks",
        "widthGrow": 1,
    }, {
        "title": "Alert",
        "formatter": ns("alertIcon"),
        "widthGrow": 1,
    }, {
        "title": "Present same day",
        "field": "present_today",
        "visible": False,
    }, {
        "title": "Authorised same day",
        "field": "authorised_today",
        "visible": False,
    }],
)
missing_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "summary",
        "tab": "missing",
    },
    options={
        "resizableColumns": False,
        "groupBy": ["date", "period"],
        "groupHeader": ns("groupHeader2"),
        "maxHeight": "60vh",
        "layout": "fitData"
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
        "title": "Date",
        "field": "date",
        "visible": False,
    }, {
        "title": "Register",
        "field": "register"
    }, {
        "title": "Period",
        "field": "period",
        "visible": False,
    }, {
        "title": "Lecturer",
        "field": "lecturer"
    }, {
        "title": "Missing marks",
        "field": "missing"
    }])

progress_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "summary",
        "tab": "progress"
    },
    options={
        "resizableColumns": True,
        "maxHeight": "70vh",
        "nestedFieldSeparator": "|" # Default is . which conflicts with some assessment names
    },
    theme='bootstrap/tabulator_bootstrap4',
    downloadButtonType={
        "css": "btn btn-primary",
        "text": "Download",
        "type": "csv"
    },
)

progress_cohort = dcc.Dropdown(id='progress-cohort-dropdown', options=[{'label': c, 'value': c} for c in ['2022', '2123']], value='2123')

validation_layout = content + [
    attendance_dashboard, unauthorised_table, missing_table, progress_cohort, progress_table
]
tab_map = {
    "summary-tab-attendance": [attendance_dashboard],
    "summary-tab-unauthorised": [dbc.Col([unauthorised_table])],
    "summary-tab-missing":
    [dbc.Col([missing_table])],
    "summary-tab-progress":
    [dbc.Col(dbc.Row([dbc.Col(progress_cohort, width=1), dbc.Col(progress_table)]))]
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
    sql_template = sql_jinja_env.get_template('sql/missing marks.sql')
    template_vars = {}
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
    sql = sql_template.render()
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


@app.callback(
    [
    Output({
        "type": "table",
        "page": "summary",
        "tab": "progress"
    }, "data"),
    Output({
        "type": "table",
        "page": "summary",
        "tab": "progress"
    }, "columns"),
    ], [
    Input("progress-cohort-dropdown", "value")
])
def update_progress_table(cohort):
    enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    student_ids = [doc.get("_id") for doc in enrolment_docs]
    assessment_docs = data.get_data("assessment", "student_id", student_ids)
    merged_df = pd.merge(
        pd.DataFrame.from_records(enrolment_docs, columns=["_id", "given_name", "family_name"]),
        pd.DataFrame.from_records(assessment_docs, columns=["student_id", "subject_name", "assessment", "grade"]),
        how='right', left_on='_id', right_on='student_id'
    ).set_index(['given_name', 'family_name', 'subject_name', 'assessment']).drop(['_id', 'student_id'], axis=1)
    # print(merged_df.loc[merged_df.index.duplicated()])
    # Need a log here if there are duplicates that will hurt unstack
    # But don't have much choice because melt will only accept one value column
    merged_df = merged_df.loc[~ merged_df.index.duplicated(keep='first')].copy()
    pivot_df = merged_df.unstack(level=-1).reset_index().fillna("").astype(str)
    flattened_columns = [a if not b else b for a,b in pivot_df.columns]
    pivot_df.columns = flattened_columns
    columns = [{"title": c.replace('_', ' ').title(), "field": c, "widthGrow": 1, "headerFilter": "input"} for c in pivot_df.columns]
    columns[2].update({"widthGrow": 2})
    return pivot_df.to_dict(orient='records'), columns
