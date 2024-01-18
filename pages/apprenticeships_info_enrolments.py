from os.path import abspath
import pyodbc
import jinja2
from configparser import ConfigParser
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
from dash import html, dcc
from icecream import ic

layout = dbc.Container([
    dcc.Store(id="store-apprenticeships-enrolments", storage_type='memory'),
    dbc.Row([
        dbc.Col(
            dbc.Select(
                id={
                    "type": "dropdown",
                    "section": "apprenticeships",
                    "page": "info",
                    "tab": "missing",
                    "name": "start"
                })),
        dbc.Col(
            dbc.Select(
                id={
                    "type": "dropdown",
                    "section": "apprenticeships",
                    "page": "info",
                    "tab": "missing",
                    "name": "standard"
                })),
        dbc.Col(
            dbc.Select(
                id={
                    "type": "dropdown",
                    "section": "apprenticeships",
                    "page": "info",
                    "tab": "missing",
                    "name": "provision"
                })),
    ]),
    dbc.Row(
        html.Div(
            id={
                "type": "html",
                "section": "apprenticeships",
                "page": "info",
                "tab": "enrolments",
            }))
])


@app.callback(Output("store-apprenticeships-enrolments", "data"), [
    Input(
        {
            "type": "button",
            "section": "apprenticeships",
            "page": "info",
            "name": "update"
        }, "n_clicks")
])
def update_enrolments_store(n_clicks):
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
    sql_template = sql_jinja_env.get_template('sql/status sheet.sql')
    template_vars = {}
    sql = sql_template.render(template_vars)
    df = pd.read_sql(sql, conn)
    store_data = df.to_dict(orient='records')
    return store_data


@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "start"
        }, "options"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "start"
        }, "value"),
], [
    Input("store-apprenticeships-enrolments", "data"),
])
def update_start_dates(store_data):
    df = pd.DataFrame.from_records(store_data)

    start_dates = df.sort_values('Start')['Start'].unique()
    options = [{"label": s, "value": s} for s in start_dates]
    selected = 'All start dates'
    return options, selected

@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "standard"
        }, "options"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "standard"
        }, "value"),
], [
    Input({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "start"
        }, "value"),
],
[
    State("store-apprenticeships-enrolments", "data")
])
def update_standards(start_date, store_data):
    df = pd.DataFrame.from_records(store_data).query("Start == @start_date")
    standards = df.sort_values('Standard')['Standard'].unique()
    options = [{"label": s, "value": s} for s in standards]
    selected = 'All standards'
    return options, selected

@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "provision"
        }, "options"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "provision"
        }, "value"),
], [
    Input({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "standard"
        }, "value"),
],
[
    State({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "start"
        }, "value"),
    State("store-apprenticeships-enrolments", "data")
])
def update_provisions(standard, start_date, store_data):
    df = pd.DataFrame.from_records(store_data).query("Start == @start_date and Standard == @standard")
    provisions = df.sort_values('Provision')['Provision'].unique()
    options = [{"label": s, "value": s} for s in provisions]
    selected = 'All provisions'
    return options, selected

@app.callback(
    Output(
        {
                "type": "html",
                "section": "apprenticeships",
                "page": "info",
                "tab": "enrolments",
        }, "children"),
[
    Input({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "provision"
        }, "value"),
],
[
    State({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "standard"
        }, "value"),
    State({
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "info",
            "tab": "missing",
            "name": "start"
        }, "value"),
    State("store-apprenticeships-enrolments", "data")
])
def update_enrolments(provision, standard, start_date, store_data):
    df = pd.DataFrame.from_records(store_data).query("Start == @start_date and Standard == @standard and Provision == @provision")
    df.set_index(["Start", "Standard", "Provision", "Age at end of August", "Status"], inplace=True)
    table = dbc.Table.from_dataframe(df.loc[(start_date, standard, provision)].reset_index())
    return table
