import pyodbc
from os.path import abspath
import jinja2
from configparser import ConfigParser
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from app import app

punctuality_monthly = dcc.Graph(id={
    "type": "graph",
    "page": "summary",
    "tab": "punctuality",
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

layout = dbc.Container(punctuality_monthly)


@app.callback(
    Output({
            "type": "graph",
            "page": "summary",
            "tab": "punctuality",
            "name": "monthly"
        }, "figure"),
           [
    Input("sixthform-attendance-store", 'data')
          ]
)
def update_punctuality_dashboard(store_data):
    config_object = ConfigParser()
    config_object.read("config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
        )
    except:
        return dash.no_update
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(abspath('.')))
    sql_template = sql_jinja_env.get_template(
        'sql/cumulative punctuality monthly.sql')
    sql = sql_template.render()
    rems_df = pd.read_sql(sql, conn)
    # For monthly graph
    monthly_df = rems_df.query('date != "Year" & student_id == "All"')
    months = list(monthly_df['date'])
    monthly_figure = go.Figure(
        data=[
            go.Bar(x=monthly_df['date'],
                   y=monthly_df['punctuality'],
                   hovertemplate="During %{x}<br>%{y}",
                   xperiod='M1',
                   xperiodalignment='middle',
                   text=monthly_df['punctuality'],
                   textposition='auto',
                   marker_color='steelblue',
                   name="Monthly"),
            go.Scatter(x=monthly_df['date'],
                       y=monthly_df['cumulative'],
                       text=monthly_df['cumulative'],
                       textposition='top center',
                       marker_color='gold',
                       hovertemplate="At end of %{x}<br>%{y}",
                       xperiod='M1',
                       xperiodalignment='end',
                       name="Year to date"),
        ],
        layout={
            "title": "Monthly average student punctuality",
            "yaxis": {
                "range": [60, 100]
            },
            "xaxis": {
                "ticklabelmode": 'period',
                "tickformat": "%b %Y",
            }
        },
    )
    return monthly_figure
