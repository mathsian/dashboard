import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import callback_context as cc

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
        "height": "70vh",
    },
    style_cell={
        "maxWidth": "20px",
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
student_list_clear_button = dbc.Button(
    id={"type": "button", "page": "student", "name": "clear"},
    children=["Clear", dbc.Badge(id={"type": "badge", "page": "student", "name": "clear"}, children="0", color="light", className="ml-1")],
              color="primary")
report = [
    html.H2(id={"type": "text", "page": "student", "tab": "report", "name": "heading"}),
    html.Div(id={"type": "text", "page": "student", "tab": "report", "name": "subheading"}),
    html.H4("Attendance"),
    html.Div(id={"type": "text", "page": "student", "tab": "report", "name": "attendance"}),
    html.H4("Academic"),
    html.Div(id={"type": "text", "page": "student", "tab": "report", "name": "academic"}),
    html.H4("Pastoral"),
    html.H6("Kudos"),
    html.Div(id={"type": "text", "page": "student", "tab": "report", "name": "kudos"}),
    html.H6("Concerns"),
    html.Div(id={"type": "text", "page": "student", "tab": "report", "name": "concern"}),
]

tabs = ["Report", "Kudos", "Concern"]
content = [
    dbc.Row([
        dbc.Col(
            width=4,
            children=dbc.Card([
                dbc.CardHeader("Student list"),
                dbc.CardBody(children=[html.Div(student_list), html.Br(), html.Div(student_list_clear_button), ])
            ],
                              style={"height": "95vh"}),
        ),
        dbc.Col(
            width=8,
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

validation_layout = html.Div(children=content + report + [student_list_clear_button, student_list])
tab_map = {
    "student-tab-report": report,
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
    Output({"type": "badge", "page": "student", "name": "clear"}, "children"),
    [Input("selected-student-ids", "data")])
def update_student_list_badge(selected_student_ids):
    return len(selected_student_ids)

@app.callback(
        [Output({
        "type": "table",
        "page": "student"
    }, "data"),
         Output({"type": "table", "page": "student"}, "selected_rows"),
         ],
    [Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value"),
     Input({
         "type": "button",
         "page": "student",
         "name": "clear",
     }, "n_clicks")],
)
def update_student_table(filter_value, n_clicks):
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], []
    for doc in enrolment_docs:
        doc["id"] = doc["_id"]
    return enrolment_docs, []

@app.callback(
[
    Output({"type": "text", "page": "student", "tab": "report", "name": "heading"}, "children"),
    Output({"type": "text", "page": "student", "tab": "report", "name": "subheading"}, "children"),
    Output({"type": "text", "page": "student", "tab": "report", "name": "attendance"}, "children"),
    Output({"type": "text", "page": "student", "tab": "report", "name": "academic"}, "children"),
    Output({"type": "text", "page": "student", "tab": "report", "name": "kudos"}, "children"),
    Output({"type": "text", "page": "student", "tab": "report", "name": "concern"}, "children"),
],
[Input("selected-student-ids", "data")])
def update_student_report(selected_student_ids):
    if not selected_student_ids:
        return "", "", "", "", "", ""
    student_id = selected_student_ids[-1]
    enrolment_doc = data.get_student(student_id)
    heading = f'{enrolment_doc.get("given_name")} {enrolment_doc.get("family_name")}'
    return heading, selected_student_ids, "", "", "", ""
