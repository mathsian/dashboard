import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import app
import data
import curriculum

# The student list is on a separate card alongside the tabs
# so that it isn't updated when the tab changes
student_list = dash_table.DataTable(
    id={
        "type": "table",
        "page": "student"
    },
    columns=[
        {
            "name": "Given Name",
            "id": "given_name"
        },
        {
            "name": "Family Name",
            "id": "family_name"
        },
    ],
    style_table={
        "overflowY": "auto",
        "height": "80vh",
    },
    style_cell={
        "textAlign": "left",
        "overflow": "hidden",
    },
    style_as_list_view=True,
    row_selectable="multi",
    sort_action="native",
    filter_action="native",
    sort_by=[{
        "column_id": "given_name",
        "direction": "asc"
    }],
)

tabs = ["Report", "Kudos", "Concern"]
content = [
    dbc.Row([
        dbc.Col(
            width=4,
            children=dbc.Card([
                dbc.CardHeader("Students"),
                dbc.CardBody(children=student_list)
            ],
                              style={"height": "95vh"}),
        ),
        dbc.Col(
            width=6,
            children=dbc.Card([
                dbc.CardHeader(
                    dbc.Tabs(
                        [
                            dbc.Tab(label=t, tab_id=f"student-tab-{t.lower()}")
                            for t in tabs
                        ],
                        id=f"student-tabs",
                        card=True,
                        active_tab=f"student-tab-{tabs[0].lower()}",
                    )),
                dbc.CardBody(id=f"student-content", children=[]) ,
            ]))
    ])
]

validation_layout = content
tab_map = {
    "student-tab-report": ["Report content"],
    "student-tab-kudos": ["Kudos content"],
    "student-tab-concern": ["Concern content"],
}


@app.callback(
    Output(f"student-content", "children"),
    [Input(f"student-tabs", "active_tab")],
)
def get_content(active_tab):
    return tab_map.get(active_tab)


@app.callback(
    Output({
        "type": "table",
        "page": "student"
    }, "data"),
    [Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value")],
)
def update_student_table(filter_value):
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return []
    return enrolment_docs
