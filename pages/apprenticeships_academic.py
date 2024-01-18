import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import data
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")


module_dropdown = dbc.DropdownMenu(id={
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
    "name": "module",
},
                                   nav=True)

page_nav = dbc.Nav([
    dbc.NavItem(module_dropdown),
],
                            fill=True)

instance_nav = dbc.Nav(id={
    "type": "nav",
    "section": "apprenticeships",
    "page": "academic",
    "name": "instances"
},
                         pills=True,
                         vertical=True,
)
layout = [
    dcc.Store("apprenticeships-academic-store", storage_type='memory'),
    dbc.Card([
        dbc.CardHeader(page_nav),
        dbc.CardBody(instance_nav)
    ]),
    ]


@app.callback([
    Output({
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
    "name": "module"}, "label"),
    Output({
    "section": "apprenticeships",
    "page": "academic",
    "type": "dropdown",
        "name": "module"}, "children"),
    Output(
        {
            "type": "nav",
            "section": "apprenticeships",
            "page": "academic",
            "name": "instances"
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
        "name": "module"}, "label"),
])
def update_results(pathname, search, module_short):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get all modules
    # This is now a list of dicts
    modules = app_data.get_module_list()
    # If module is in state, default to it else pick the first from the list
    module_short = module_short or modules[0].get('short')
    # Get module from query and use it if valid
    if module_query := search_dict.get('module', False):
        if module_query[0] in [m.get('short') for m in modules]:
            module_short = module_query[0]
    # Build module selector options
    module_select_items = []
    for m in modules:
        s = urlencode(query={'module': m.get('short')})
        module_select_items.append(dbc.DropdownMenuItem(f'{m.get("short")}: {m.get("name")}', href=f'{pathname}?{s}'))
    # Get module instances
    instances = [i for i in app_data.get_instances_of_module(module_short) if i.get('id', None)]
    instance_nav_items = []
    if len(instances):
        # default to first instance
        instance_dict = instances[0]
        # If instance is in query and valid, use it
        if instance_query := search_dict.get("instance", False):
            matching_instances = [i for i in instances if i.get("code") == instance_query[0]]
            if matching_instances:
                instance_dict = matching_instances[0]
        # Generate nav of modules
        for i_dict in instances:
            q = urlencode(query={
                'module': i_dict.get("short"),
                'instance': i_dict.get("code")
            })
            active = 'exact' if i_dict.get("code") == instance_dict.get("code") else False
            instance_nav_items.append(
                dbc.NavItem(dbc.NavLink(f'{i_dict.get("code")}: {i_dict.get("start_date")}', href=f'{pathname}?{q}',
                                        active=bool(active)))
                )

    else:
        instance_dict = {}
    store_data = {
        "instance_code": instance_dict.get("code", False),
        }
    return module_short, module_select_items, instance_nav_items, store_data
