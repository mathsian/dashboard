import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from app import app

name = "summary"

content = [
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label=f"{name}-tab-{t}", tab_id=f"{name}-tab-{t}")
                        for t in ["a", "b", "c"]
                    ],
                    id=f"{name}-tabs",
                    card=True,
                    active_tab=f"{name}-tab-a",
                )
            ),
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(width=3, children=html.Div(id=f"{name}-sidebar")),
                        dbc.Col(width=7, children=html.Div(id=f"{name}-main")),
                        dbc.Col(width=2, children=html.Div(id=f"{name}-panel")),
                    ]
                )
            ),
        ]
    )
]

validation_layout = content
@app.callback(
    [
        Output(f"{name}-sidebar", "children"),
        Output(f"{name}-main", "children"),
        Output(f"{name}-panel", "children"),
    ],
    [Input(f"{name}-tabs", "active_tab"),
     Input({"type": "filter-dropdown", "filter": ALL}, "value"),
     Input("store-data", "data")],
)
def get_content(active_tab, filter_value, store_data):
    return [
        get_sidebar(active_tab, filter_value, store_data),
        get_main(active_tab, filter_value, store_data),
        get_panel(active_tab, filter_value, store_data),
    ]


def get_sidebar(active_tab, filter_value, store_data):
    return f"{name} {active_tab} sidebar"


def get_main(active_tab, filter_value, store_data):
    return f"{name} {active_tab} {filter_value} {store_data}"


def get_panel(active_tab, filter_value, store_data):
    return f"{name} {active_tab} panel"
