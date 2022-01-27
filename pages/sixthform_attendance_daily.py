import dash_tabulator
import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from app import app
from dash_extensions.javascript import Namespace
from datetime import date

ns = Namespace("myNameSpace", "tabulator")

daily_table = dash_tabulator.DashTabulator(
    id={
        "section": "sixthform",
        "type": "table",
        "page": "attendance",
        "tab": "unauthorised",
    },
    options={
        "resizableColumns": False,
        "height": "70vh",
        "clipboard": "copy",
        # "pagination": "local",
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
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
        "topCalc": "count",
        "widthGrow": 1,
    }],
)

date_picker = dcc.DatePickerSingle(
    id={"section": "sixthform",
        "page": "attendance",
        "tab": "daily",
        "type": "date"},
    date=date.today(),
    display_format="MMM D, YY"
)
layout = dbc.Container([
    dbc.Row([
        dbc.Col(date_picker)
    ]),
    dbc.Row([
        dbc.Col(daily_table)
    ])], fluid=True)

@app.callback(
    Output(
{
        "section": "sixthform",
        "type": "table",
        "page": "attendance",
        "tab": "unauthorised",
    }, "data"
    ),
[Input(
{"section": "sixthform",
        "page": "attendance",
        "tab": "daily",
        "type": "date"}, "date"
)])
def update_daily_table(date_selected):
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
    sql_template = sql_jinja_env.get_template('sql/sixthform_day_absentees.sql')
    sql = sql_template.render({"date": date_selected})
    df = pd.read_sql(sql, conn)
    return df.to_dict(orient='records')

