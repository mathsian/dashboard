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

results_table = dash_tabulator.DashTabulator(
        id={
                "section": "apprenticeships",
                "page": "reports",
                "tab": "results",
                "type": "table",
                "name": "results"
            },
        theme='bootstrap/tabulator_bootstrap4',
        options={
            "resizableColumns": False,
            "height": "70vh",
            "clipboard": "copy",
            "layout": "fitData"
        }
    )

layout = dbc.Container([dbc.Row([dbc.Col([dcc.Loading(results_table)])])])


@app.callback(
    [
    Output(
        {
            "section": "apprenticeships",
            "page": "reports",
            "tab": "results",
            "type": "table",
            "name": "results"
        }, "columns"),
    Output(
        {
            "section": "apprenticeships",
            "page": "reports",
            "tab": "results",
            "type": "table",
            "name": "results"
        }, "data"),
    ],[
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
    # drop if name is None - learners with no module results yet
    results_df = pd.DataFrame.from_records(results).sort_values(['level', 'start_date', 'family_name', 'given_name' ]).dropna(subset=['name', 'short'])
    # results_df['Class'] = pd.Categorical(
    #     results_df['mark'].fillna(-1).apply(lambda t: get_class(t)),
    #     ['TBA', 'Fail', 'Pass', 'Merit', 'Distinction'])
    results_df = results_df.drop_duplicates(subset=['family_name', 'given_name', 'level', 'name', 'short'], keep='last')
    results_df = results_df.set_index(['family_name', 'given_name', 'level', 'name', 'short'])['mark']
    results_df = results_df.unstack(['level', 'name', 'short'], fill_value="")
    results_df.index.set_names(['Family name', 'Given name'], inplace=True)
    group_columns = [
        {"title": l,
         "columns": [
            {
                "title": s,
                "field": s,
                "headerTooltip": n,
            } for (n,s) in results_df[(l,)].columns
        ]} for l in results_df.columns.unique(0)
    ]
    columns=[
        {
            "title": "Family name",
            "field": "Family name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
            "frozen": True
        },
        {
            "title": "Given name",
            "field": "Given name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
            "frozen": True
        },
    ] + group_columns
    results_df.columns = [s for l,n,s in results_df.columns]
    data = results_df.reset_index().to_dict(orient='records')
    return columns, data
