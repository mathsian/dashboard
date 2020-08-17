"""
Owns top level tabs, dropdowns, container and storage
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import curriculum

dropdowns = html.Div(
    id="div-dropdowns",
    children=[
        html.Div(
            id="div-dropdown-cohort",
            children=[
                dcc.Dropdown(
                    id="dropdown-cohort",
                    options=curriculum.cohorts["options"],
                    value=curriculum.cohorts["default"],
                    multi=True,
                )
            ],
        ),
        html.Div(
            id="div-dropdown-subject",
            children=[
                dcc.Dropdown(
                    id="dropdown-subject",
                    options=curriculum.subjects["options"],
                    value=curriculum.subjects["default"],
                )
            ],
        ),
        html.Div(
            id="div-dropdown-assessment",
            children=[
                dcc.Dropdown(
                    id="dropdown-assessment",
                    options=curriculum.assessments["options"],
                    value=curriculum.assessments["default"],
                )
            ],
        ),
    ],
)

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


# Top level container
layout = dbc.Container(
    [
        dcc.Store(id="store-student", storage_type="memory", data={}),
        dcc.Store(id="store-student-data", storage_type="memory", data={}),
        dcc.Store(id="store-assessment-data", storage_type="memory", data={}),
        dcc.Store(id="store-attendance-data", storage_type="memory", data={}),
        dcc.Store(id="store-kudos-data", storage_type="memory", data={}),
        dcc.Store(id="store-concern-data", storage_type="memory", data={}),
        html.Div(id="div-header"),
        dbc.Row(
            [
                dbc.Col(
                    id="div-sidebar",
                    children=[dropdowns, html.Div(id="div-sidebar-content")],
                    width=2,
                ),
                dbc.Col(
                    id="div-main",
                    children=[
                        html.Div(id="div-tabs-main", children=tabs_main),
                        html.Div(id="div-tabs-sub"),
                        dbc.Row(
                            [
                                html.Div(id="div-main-content"),
                                html.Div(id="div-panel-content"),
                            ]
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)
