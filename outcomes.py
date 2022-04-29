import dash
from dash import html
from dash import dcc
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
sql_template = sql_jinja_env.get_template('sql/outcomes individual.sql')
template_vars = {}
sql = sql_template.render(template_vars)
df = pd.read_sql_query(sql, conn, dtype='str')
levels = ["STEN_Year", "stem_expctd_end_date", "LEARNING_AIM_TITLE"]
df = df.sort_values(by=levels+["STUD_Surname", "STUD_Forename_1"])
df = df.set_index(levels)

first_level_values = list(df.index.unique(0))
first_level_dropdown = dcc.Dropdown(id="first_level_dropdown",
                                  options=[{"label": y, "value": y} for y in
                                  ["All"] + first_level_values],
                                           value=first_level_values[0],
                                    clearable=True)
second_level_dropdown = dcc.Dropdown(id="second_level_dropdown", clearable=True)
third_level_dropdown = dcc.Dropdown(id="third_level_dropdown", clearable=True)
results_table = DashTabulator(id="results_table", columns=[{"title": c,
    "field": c} for c in df.reset_index().columns],
    downloadButtonType = {"css": "btn btn-primary", "text":"Export",
        "type":"csv"})

app.layout = dbc.Container(
    children=[
        dbc.Row([dbc.Col(levels[0], width=2), dbc.Col(first_level_dropdown)]),
        dbc.Row([dbc.Col(levels[1], width=2), dbc.Col(second_level_dropdown)]),
        dbc.Row([dbc.Col(levels[2], width=2), dbc.Col(third_level_dropdown)]),
        dbc.Row(dbc.Col(results_table))
        ], fluid=True)

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
    print(first_level_value, second_level_value, third_level_value)
    keys = [v for v in [first_level_value,
        second_level_value, third_level_value] if v]
    key_levels = [i for i,v in enumerate([first_level_value,
        second_level_value, third_level_value]) if v]
    result = df.xs(key=keys, level=key_levels, drop_level=False).reset_index()
    return result.to_dict(orient='records')

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
def populate_third_level(second_level_value, first_level_value):
    keys = [v for v in [first_level_value, second_level_value] if v]
    key_levels = [i for i,v in enumerate([first_level_value,
        second_level_value]) if v]
    third_level_values = df.xs(key=keys, level=key_levels,
            drop_level=False).index.unique(2)
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
def populate_second_level(first_level_value):
    if first_level_value:
        second_level_values = df.loc[first_level_value].index.unique(0)
    else:
        second_level_values = df.index.unique(1)
    return [{"label": i, "value": i} for i in second_level_values], second_level_values[0]

if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
