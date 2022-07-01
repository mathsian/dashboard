import dash_tabulator
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
from app import app
import app_data

results_table = html.Div(
    id={
        "section": "apprenticeships",
        "page": "reports",
        "tab": "results",
        "type": "table",
        "name": "results"
    })
layout = dbc.Container([dbc.Row([dbc.Col([results_table])])])


@app.callback(
    Output(
        {
            "section": "apprenticeships",
            "page": "reports",
            "tab": "results",
            "type": "table",
            "name": "results"
        }, "children"), [
            Input(
                {
                    "type": "storage",
                    "section": "apprenticeships",
                    "page": "reports",
                    "name": "results"
                }, 'data')
        ])
def update_table(results):
    if not results:
        return "No results for these learners."
    results_df = pd.DataFrame.from_records(results).sort_values(['level', 'start_date', 'family_name', 'given_name' ])
    # results_df['Class'] = pd.Categorical(
    #     results_df['mark'].fillna(-1).apply(lambda t: get_class(t)),
    #     ['TBA', 'Fail', 'Pass', 'Merit', 'Distinction'])
    results_df = results_df.drop_duplicates(subset=['family_name', 'given_name', 'level', 'name'], keep='last')
    results_df = results_df.set_index(['family_name', 'given_name', 'level', 'name'])['mark']
    results_df = results_df.unstack(['level', 'name'], fill_value="")
    results_df.index.set_names(['Family name', 'Given name'], inplace=True)
    return dbc.Table.from_dataframe(results_df, index=True, responsive=True)


def get_class(mark):
    if mark >= 69.5:
        return 'Distinction'
    elif mark >= 59.5:
        return 'Merit'
    elif mark >= 39.5:
        return 'Pass'
    elif mark >= 0:
        return 'Fail'
    else:
        return 'TBA'
