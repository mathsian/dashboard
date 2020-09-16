"""
Layout for subject-focused data
"""
import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import data
import plotly.graph_objects as go
import curriculum

subject_graph = html.Div(
    id="content-subject-view", children=dcc.Graph(id="subject-graph"),
)
subject_table = html.Div(
    id="content-subject-edit",
    children=dash_table.DataTable(
        id="subject-table",
        columns=[
            {"name": "Given name", "id": "given_name"},
            {"name": "Family name", "id": "family_name"},
            {"name": "Grade", "id": "grade", "presentation": "dropdown", "editable": True},
        ],
    ),
)
subtabs = html.Div(
    id="div-subtabs-subject",
    children=dcc.Tabs(
        id={"type": "tabs-sub", "id": "subject"},
        children=[
            dcc.Tab(value="tab-subject-view", label="View"),
            dcc.Tab(value="tab-subject-edit", label="Edit"),
        ],
        value="tab-subject-view",
    ),
)

content = [subject_graph, subject_table]
sidebar = [html.Div()]
panel = [html.Div(
    id="div-panel-subject",
    children=html.Button(
        "Save",
        id="subject-save-button",
        n_clicks=0
        ),
    )]


def register_callbacks(app):
    @app.callback(
        Output("div-subtabs-subject", "hidden"), [Input("tabs-main", "value")]
    )
    def subject_hide_subtabs(value):
        return value != "tab-main-subject"

    @app.callback(
        [
            Output("content-subject-view", "hidden"),
            Output("content-subject-edit", "hidden"),
            Output("div-panel-subject", "hidden"),
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "subject"}, "value"),
        ],
    )
    def subject_hide_content(main_value, sub_value):
        if main_value != "tab-main-subject":
            return True, True, True
        else:
            return (sub_value != "tab-subject-view",
                    sub_value == "tab-subject-view",
                    sub_value == "tab-subject-view",)

    @app.callback(
        [Output("subject-graph", "figure"),Output("subject-table", "data"), Output("subject-table", "dropdown")],
        [
            Input({"type": "filter-dropdown", "id": "subject"}, "value"),
            Input({"type": "filter-dropdown", "id": "assessment"}, "value"),
            Input("store-data", "data"),
        ],
    )
    def update_subject_graph(
        subject_value, assessment_value, store_data,
    ):

        subject_df = pd.DataFrame.from_records(store_data.get("assessment"), columns=["_id", "_rev", "subtype", "subject", "student_id", "assessment", "grade", "date"]).query(
            "(subject==@subject_value) and (assessment==@assessment_value)"
        )
        subtype = subject_df.iloc[0]["subtype"]
        student_id_list = subject_df.student_id.unique()
        student_df = pd.DataFrame.from_records(data.get_students(student_id_list), columns=["_id", "given_name", "family_name", "aps"])
        merged_df = pd.merge(
            subject_df, student_df, how="left", left_on="student_id", right_on="_id"
        )
        grade_array = curriculum.scales.get(subtype)
        figure_scatter = {
            "data": [
                go.Scatter(x=merged_df["aps"], y=merged_df["grade"],
                mode='markers', text=merged_df["given_name"])
            ],
            "layout": go.Layout(
                title=f"{subject_value}:{assessment_value}",
                yaxis={
                    "type": "category",
                    "range": [0, len(grade_array)],
                    "categoryorder": "array",
                    "categoryarray": grade_array
                })
        }
        figure_bar = {
            "data": [
go.Histogram(x=merged_df["grade"], histfunc="count")
            ],
            "layout": go.Layout(
                title=f"{subject_value}:{assessment_value}",
                xaxis={
                    "type": "category",
                    "range": [0, len(grade_array)],
                    "categoryorder": "array",
                    "categoryarray": grade_array
                }
            )
        }
        return figure_bar, merged_df.to_dict(orient="records"), {"grade": {"options": [{"label": g, "value": g} for g in grade_array]}}
