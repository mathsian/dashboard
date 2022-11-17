from flask import request
import dash_tabulator
import dash
from dash.dash import no_update
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
import app_data
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

layout = dbc.Row(dbc.Col(html.Div(id={
    "type": "div",
    "section": "apprenticeships",
    "page": "info",
    "tab": "missing"
})))


@app.callback(
    Output({
        "type": "div",
        "section": "apprenticeships",
        "page": "info",
        "tab": "missing",
    }, "children"), [
        Input(
            {
                "type": "button",
                "section": "apprenticeships",
                "page": "info",
                "name": "update"
            }, "n_clicks")
    ])
def get_missing_results(n_clicks):
    null_results = app_data.get_null_results()
    null_results_df = pd.DataFrame.from_records(null_results)
    null_results_df['link'] = null_results_df.apply(lambda row: f"https://data.ada.ac.uk/apprenticeships/academic/edit?module={row['name'].replace(' ','+')}&instance={row['code']}", axis=1)
    null_results_records = null_results_df.to_dict(orient='records')
    null_results_th = html.Thead(html.Tr([html.Td("Module"), html.Td("Missing results")]))
    null_results_td = html.Tbody([html.Tr([html.Td(html.A(r.get("code"), href=r.get("link"))), html.Td(r.get("count"))]) for r in null_results_records])
    null_results_table = dbc.Table([null_results_th] + [null_results_td])
    return null_results_table
