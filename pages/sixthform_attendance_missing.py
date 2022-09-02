import dash_tabulator
import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

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
        # "maxHeight": "70vh",
        # "layout": "fitData"
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[{
        "title": "Date",
        "field": "date",
        "visible": False,
    }, {
        "title": "Register",
        "field": "register",
        "headerSort": False,
    }, {
        "title": "Period",
        "field": "period",
        "visible": False,
    }, {
        "title": "Lecturer",
        "field": "lecturer",
        "headerSort": False,
    }, {
        "title": "Missing marks",
        "field": "Student ID",
        "headerSort": False,
    }, {
        "title": "Students",
        "field": "Student",
        "headerSort": False,
    }])

layout = dbc.Container(missing_table, fluid=True)

@app.callback(
    Output({
        "type": "table",
        "page": "summary",
        "tab": "missing",
    }, "data"), [
        Input(
            {
                "type": "button",
                "section": "sixthform",
                "page": "attendance",
                "name": "update"
            }, "n_clicks")
    ])
def update_missing_table(n_clicks):
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
    df['Student'] = df['Student ID'] + " " + df['Given Name'] + " " + df['Family Name']
    grouped_df = df.groupby(['date', 'period', 'register', 'lecturer'], as_index=False).agg(
    {'Student ID': 'count',
     'Student': ', '.join})
    grouped_df.sort_values(by='date', ascending=False, inplace=True)
    return grouped_df.to_dict(orient='records')
