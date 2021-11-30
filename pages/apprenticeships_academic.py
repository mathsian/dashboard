import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")


cohort_dropdown = dbc.DropdownMenu(id={
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
    "name": "cohort"}, nav=True)

# intake_dropdown = dbc.DropdownMenu(id={
#     "section": "apprenticeships",
#     "page": "academic",
#     "type": "dropdown",
#     "name": "intake"}, nav=True)

page_nav = dbc.Nav([
    dbc.NavItem(cohort_dropdown),
#    dbc.NavItem(intake_dropdown),
],
                            fill=True)

module_nav = dbc.Nav(id={
    "type": "nav",
    "section": "apprenticeships",
    "page": "academic",
    "name": "modules"
},
                         pills=True,
                         vertical=True,
)
layout = [
    dcc.Store("apprenticeships-academic-store", storage_type='memory'),
    dbc.Row(dbc.Col(page_nav)),
    dbc.Row(dbc.Col(module_nav))
    ]


@app.callback([
    Output({
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
    "name": "cohort"}, "label"),
    Output({
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
        "name": "cohort"}, "children"),
#     Output({
#     "section": "apprenticeships",
#     "page": "academic",
#     "type": "dropdown",
#     "name": "intake"}, "label"),
#     Output({
#     "section": "apprenticeships",
#     "page": "academic",
#     "type": "dropdown",
#     "name": "intake"}, "children"),
    Output(
        {
            "type": "nav",
            "section": "apprenticeships",
            "page": "academic",
            "name": "modules"
        }, "children"),
    Output("apprenticeships-academic-store", "data")
], [
    Input("location", "pathname"),
    Input("location", "search"),
], [
    State({
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
        "name": "cohort"}, "label"),
#     State({
#     "section": "apprenticeships",
#     "page": "academic",
#     "type": "dropdown",
#     "name": "intake"}, "label"),
])
def update_results(pathname, search, cohort):
    search_dict = parse_qs(search.removeprefix('?'))

    # Get all cohorts
    cohorts = [c.get('key') for c in data.get_grouped_data("apprentice", "cohort_grouped", 0, 'ZZZ', db_name='app_testing')]
    # Get cohort from query, or current state, or first cohort
    cohort = search_dict.get('cohort', [cohort])[0] or cohorts[0]
    # Build cohort selector options
    cohort_select_items = [] 
    for c in cohorts:
        s = urlencode(query={'cohort': c})
        cohort_select_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))

    # Get list of relevant apprentices
    apprentice_docs = data.get_data("apprentice", "cohort", [cohort], db_name='app_testing')
    apprentice_df = pd.DataFrame.from_records(apprentice_docs, columns=data.APPRENTICE_SCHEMA)
    # Get results for given cohort
    result_docs = data.get_data("result", "student_id", [a.get("_id") for a in apprentice_docs], db_name='app_testing')
    result_df = pd.DataFrame.from_records(result_docs, columns=data.RESULT_SCHEMA).sort_values('moduleName')
    # missing total values make that field an object where we want an int
    result_df["total"] = pd.to_numeric(result_df["total"], errors='coerce')
    # assign class
    result_df["class"] = pd.cut(result_df["total"], bins=[-1, 39.5, 59.5, 69.5, 101], labels=['Fail', 'Pass', 'Merit', 'Distinction'])
    result_df["class"].values.add_categories("Missing", inplace=True)
    result_df["class"].fillna("Missing", inplace=True)
    # drop=False so the column is still there to match the schema
    merged_df = pd.merge(result_df, apprentice_df, left_on='student_id', right_on='_id', how='left').set_index(['moduleCode', 'moduleName'], drop=False)
    moduleCodes = merged_df.index.unique()

    module_nav_items = []
    if len(moduleCodes):
        # Get module from query or first result
        module = search_dict.get("module", moduleCodes[0])[0]
        # Generate nav of modules
        for m, n in moduleCodes:
            q = urlencode(query={
                'cohort': cohort,
                'module': m
            })
            active = 'exact' if m == module else False
            module_nav_items.append(
                dbc.NavItem(dbc.NavLink(n + ": " + m, href=f'{pathname}?{q}',
                                        active=bool(active)))
                )

        module_results_df = merged_df.loc[[module]] # pass list
        result_docs = module_results_df.to_dict(orient='records')
    else:
        # Learners have no modules yet
        module = ""
        result_docs = []
    store_data = {
        "result_docs": result_docs,
        "module": module
        }
    return cohort, cohort_select_items, module_nav_items, store_data
