import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
from app import app
import data
import plotly.graph_objects as go
import curriculum

tabs = ["View", "Edit"]
content = [
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=t, tab_id=f"academic-tab-{t.lower()}")
                    for t in tabs
                ],
                id=f"academic-tabs",
                card=True,
                active_tab=f"academic-tab-{tabs[0].lower()}",
            )),
        dbc.CardBody(dbc.Row(id="academic-content")),
    ])
]
subject_table = dash_table.DataTable(id={
    "type": "table",
    "page": "academic",
    "tab": "edit"
},
                                     columns=[
                                         {
                                             "name": "Given name",
                                             "id": "given_name",
                                             "editable": False
                                         },
                                         {
                                             "name": "Family name",
                                             "id": "family_name",
                                             "editable": False
                                         },
                                         {
                                             "name": "Grade",
                                             "id": "grade",
                                             "type": "text",
                                             "presentation": "dropdown",
                                             "editable": True
                                         },
                                         {
                                             "name": "Comment",
                                             "id": "comment",
                                             "type": "text",
                                             "presentation": "input",
                                             "editable": True
                                         },
                                     ],
                                     sort_action='native',
                                     filter_action='native',
                                     sort_by=[{
                                         "column_id": "given_name",
                                         "direction": "asc"
                                     }, {
                                         "column_id": "family_name",
                                         "direction": "asc"
                                     }])

assessment_filter = dcc.Dropdown(id={
    "type": "dropdown",
    "page": "academic",
    "name": "assessment"
}, )
validation_layout = content + [subject_table, assessment_filter]
tab_map = {
    "academic-tab-view": [dbc.Col([assessment_filter])],
    "academic-tab-edit":
    [dbc.Col([assessment_filter, html.Br(), subject_table])]
}


@app.callback(
    Output(f"academic-content", "children"),
    [
        Input(f"academic-tabs", "active_tab"),
    ],
)
def get_content(active_tab):
    return tab_map.get(active_tab)


@app.callback([
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data"),
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "dropdown"),
], [Input({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_subject_table(filter_value):
    cohort, _, group_id = filter_value
    if not (cohort and group_id):
        return [], {}
    group_df = pd.DataFrame.from_records(
        data.get_data("group", "group_id", group_id))
    student_ids = group_df["student_id"].tolist()
    enrolment_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "_id", student_ids))
    return enrolment_df.to_dict(orient='records'), {}


@app.callback([
    Output({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "options"),
    Output({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "value")
], [Input({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_assessment_dropdown(filter_value):
    cohort, _, group_id = filter_value
    if not (cohort and group_id):
        return [], ""
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "group_id", group_id))
    assessment_list = assessment_df.sort_values(
        by="date", ascending=False)["assessment"].unique().tolist()
    options = [{"label": a, "value": a} for a in assessment_list]
    return options, options[0].get("value")
