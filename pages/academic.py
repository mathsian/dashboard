import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from app import app

tabs = ["View", "Edit"]
content = [
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label=t, tab_id=f"academic-tab-{t.lower()}")
                        for t in tabs
                    ],
                    id=f"academic-tabs",
                    card=True,
                    active_tab=f"academic-tab-{tabs[0].lower()}",
                )
            ),
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(width=3, children=html.Div(id=f"academic-sidebar")),
                        dbc.Col(width=7, children=html.Div(id=f"academic-main")),
                        dbc.Col(width=2, children=html.Div(id=f"academic-panel")),
                    ]
                )
            ),
        ]
    )
]

validation_layout = content

@app.callback(
    [
        Output(f"academic-sidebar", "children"),
        Output(f"academic-main", "children"),
        Output(f"academic-panel", "children"),
    ],
    [Input(f"academic-tabs", "active_tab"),],
)
def get_content(active_tab):
    return "", "", ""
