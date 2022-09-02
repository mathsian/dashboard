import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
from dash import dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

update_button =  dbc.Button(children="Update",
                   id={
                       "type": "button",
                       "section": "sixthform",
                       "page": "attendance",
                       "name": "update"
                   },
                   outline=True,
                   color='primary')
gauge_last = daq.Gauge(
    id={
        "type": "gauge",
        "section": "sixthform",
        "page": "attendance",
        "name": "last"
    },
    label="This month",
    labelPosition="top",
    scale={
        "start": 0,
        "interval": 5,
        "labelInterval": 4,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
    size=170,
    style={'margin-bottom': -60},
)
gauge_cumulative = daq.Gauge(
    id={
        "type": "gauge",
        "section": "sixthform",
        "page": "attendance",
        "name": "cumulative"
    },
    label="This Year",
    labelPosition="top",
    scale={
        "start": 0,
        "interval": 5,
        "labelInterval": 4,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
    size=170,
)

layout = [
    dcc.Store(id='sixthform-attendance-store', storage_type='memory'),
    dbc.Row(dbc.Col(update_button)),
    dbc.Row(dbc.Col(gauge_last)),
    dbc.Row(dbc.Col(gauge_cumulative))
]


@app.callback([
    Output(
        {
            "type": "gauge",
            "section": "sixthform",
            "page": "attendance",
            "name": "last"
        }, 'value'),
    Output(
        {
            "type": "gauge",
            "section": "sixthform",
            "page": "attendance",
            "name": "cumulative"
        }, 'value'),
    Output("sixthform-attendance-store", 'data')
], [
    Input(
        {
            "type": "button",
            "section": "sixthform",
            "page": "attendance",
            "name": "update"
        }, 'n_clicks')
])
def update_attendance_data(n_clicks):
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

    cumulative_value = rems_df.query(
        'student_id == "All" & date == "Year"')["attendance"].iat[0]
    last_value = rems_df.query('date != "Year"').query(
        'student_id == "All" & date == date.max()')["attendance"].iat[0]

    store_data = rems_df.to_dict(orient='records')
    return last_value, cumulative_value, store_data
