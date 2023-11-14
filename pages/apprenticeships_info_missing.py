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
    missing_results = app_data.get_missing_results()
    missing_results_df = pd.DataFrame.from_records(missing_results)
    missing_results_df['link'] = missing_results_df.apply(lambda row: f"https://data.ada.ac.uk/apprenticeships/academic/edit?module={row['short'].replace(' ','+')}&instance={row['code']}", axis=1)
    missing_results_records = missing_results_df.to_dict(orient='records')
    missing_results_th = html.Thead(html.Tr([html.Td("Module"), html.Td("Missing results")]))
    missing_results_td = html.Tbody([html.Tr([html.Td(html.A(r.get("code"), href=r.get("link"))), html.Td(r.get("count"))]) for r in missing_results_records])
    missing_results_table = dbc.Table([missing_results_th] + [missing_results_td])
    return missing_results_table
