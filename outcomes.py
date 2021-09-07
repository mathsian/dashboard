import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_tabulator import DashTabulator
import pandas as pd
import pyodbc
import jinja2
from os.path import abspath
from configparser import ConfigParser

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Get connection settings
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
sql_template = sql_jinja_env.get_template('sql/outcomes.sql')
template_vars = {}
sql = sql_template.render(template_vars)
df = pd.read_sql_query(sql, conn, dtype='str')
levels = ["LEARNING_AIM_TITLE", "STEN_Provision_Instance", "STEN_Year", ]
df = df.sort_values(by=levels+["STUD_Surname", "STUD_Forename_1"])
df = df.set_index(levels)

first_level_values = df.index.unique(0)
first_level_dropdown = dcc.Dropdown(id="first_level_dropdown",
                                  options=[{"label": y, "value": y} for y in first_level_values],
                                           value=first_level_values[0],
                                    clearable=False)
second_level_dropdown = dcc.Dropdown(id="second_level_dropdown", clearable=False)
third_level_dropdown = dcc.Dropdown(id="third_level_dropdown", clearable=False)
results_table = DashTabulator(id="results_table", columns=[{"title": c, "field": c} for c in df.columns] )

app.layout = dbc.Container(
    children=[
        dbc.Row(dbc.Col(first_level_dropdown)),
        dbc.Row(dbc.Col(second_level_dropdown)),
        dbc.Row(dbc.Col(third_level_dropdown)),
        dbc.Row(dbc.Col(results_table))
        ])

@app.callback(
    Output("results_table", "data"),
[
    Input("third_level_dropdown", "value")
],
[
    State("first_level_dropdown", "value"),
    State("second_level_dropdown", "value")
])
def populate_content(third_level_value, first_level_value, second_level_value):
    return df.loc[first_level_value, second_level_value, third_level_value].to_dict(orient='records')

@app.callback(
    [
    Output("third_level_dropdown", "options"),
    Output("third_level_dropdown", "value"),
        ],
[
    Input("second_level_dropdown", "value")
],
[
    State("first_level_dropdown", "value"),
])
def populate_prpi_options(second_level_value, first_level_value):
    third_level_values = df.loc[first_level_value].loc[second_level_value].index.unique(0)
    return [{"label": t, "value": t} for t in third_level_values], third_level_values[0]

@app.callback(
    [
    Output("second_level_dropdown", "options"),
    Output("second_level_dropdown", "value"),
    ],
    [
    Input("first_level_dropdown", "value"),
    ]
)
def populate_provision_options(first_level_value):
    second_level_values = df.loc[first_level_value].index.unique(0)
    return [{"label": i, "value": i} for i in second_level_values], second_level_values[0]

if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
