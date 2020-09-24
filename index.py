"""
Owns top level tabs, dropdowns, container and storage
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import curriculum
from pages import cohort, team, subject, student
from flask import session

sidebar = [
    html.Div(
        id="div-dropdown-cohort",
        children=[
            dcc.Dropdown(
                id={"type": "filter-dropdown", "id": "cohort"},
                options=curriculum.cohorts_dropdown["options"],
                value=curriculum.cohorts_dropdown["default"],
                multi=False,
            )
        ],
    ),
    html.Div(
        id="div-dropdown-team",
        children=[
            dcc.Dropdown(
                id={"type": "filter-dropdown", "id": "team"},
                placeholder="Select a team",
                multi=True,
            )
        ],
    ),
    html.Div(
        id="div-dropdown-subject",
        children=[
            dcc.Dropdown(
                id={"type": "filter-dropdown", "id": "subject"},
                placeholder="Select a subject",
            )
        ],
    ),
    html.Div(
        id="div-dropdown-assessment",
        children=[
            dcc.Dropdown(
                id={"type": "filter-dropdown", "id": "assessment"},
                placeholder="Select an assessment",
            )
        ],
    ),
    html.Br(),
    html.Div(
        id="div-sidebar-content",
        children=cohort.sidebar + team.sidebar + subject.sidebar + student.sidebar,
    ),
]

tabs_main = dcc.Tabs(
    id="tabs-main",
    value="tab-main-cohort",
    children=[
        dcc.Tab(value="tab-main-cohort", label="Cohort"),
        dcc.Tab(value="tab-main-team", label="Team"),
        dcc.Tab(value="tab-main-subject", label="Subject"),
        dcc.Tab(value="tab-main-student", label="Student"),
    ],
)

main_content = cohort.content + team.content + subject.content + student.content
panel_content = cohort.panel + team.panel + subject.panel + student.panel
layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.Div(id="div-header"))),
        dbc.Row(
            [
                dbc.Col(sidebar, width=3),
                dbc.Col(
                    [
                        dbc.Row(dbc.Col(html.Div(tabs_main), width=9)),
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [cohort.subtabs, team.subtabs, subject.subtabs, student.subtabs],
                                width=9,
                            )
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        id="div-main-content", children=main_content
                                    ),
                                    width=8,
                                ),
                                dbc.Col(
                                    html.Div(
                                        id="div-panel-content", children=panel_content
                                    ),
                                    width=2,
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        dcc.Store(id="store-data", storage_type="memory", data={}),
        dcc.Store(id="store-student", storage_type="memory", data={}),
    ],
    fluid=True,
)
def register_callbacks(app):

    @app.callback(
        [Output({"type": "filter-dropdown", "id": "team"}, "options"),
         Output({"type": "filter-dropdown", "id": "subject"}, "options"),
         Output({"type": "filter-dropdown", "id": "assessment"}, "options"),
         Output("div-header", "children"),],
    [Input("store-data", "data")])
    def update_dropdowns(store_data):
        teams = pd.DataFrame.from_records(store_data.get("student"), columns=["team"])["team"].unique()
        groups = pd.DataFrame.from_records(store_data.get("group"), columns=["name"])["name"].unique()
        assessments = pd.DataFrame.from_records(store_data.get("assessment"), columns=["assessment"])["assessment"].unique()
        user_email = session.get('email', "no email recorded")
        return [{"label": t, "value": t} for t in teams], [{"label": g,
            "value": g} for g in groups], [{"label": a, "value": a} for a in
                assessments], user_email
