import dash_tabulator
import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from app import app
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

unauthorised_table = dash_tabulator.DashTabulator(
    id={
        "section": "sixthform",
        "type": "table",
        "page": "attendance",
        "tab": "unauthorised",
        "name": "unauthorised_table"
    },
    options={
        "resizableColumns": False,
        "groupBy": "date",
        # "layout": "fitData",
        # "maxHeight": "70vh",
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

layout = dbc.Container(unauthorised_table, fluid=True)

@app.callback(
    Output({
        "type": "table",
        "section": "sixthform",
        "page": "attendance",
        "tab": "unauthorised",
        "name": "unauthorised_table"
    }, "data"), [
        Input(
            {
                "type": "button",
                "section": "sixthform",
                "page": "attendance",
                "name": "update"
            }, "n_clicks")
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
