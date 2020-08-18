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
            {"name": "Grade", "id": "grade"},
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
panel = [html.Div()]


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
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "subject"}, "value"),
        ],
    )
    def subject_hide_content(main_value, sub_value):
        if main_value != "tab-main-subject":
            return True, True
        else:
            return (sub_value != "tab-subject-view", sub_value != "tab-subject-edit")

    @app.callback(
        [Output("subject-graph", "figure"), Output("subject-table", "data")],
        [
            Input({"type": "filter-dropdown", "id": "cohort"}, "value"),
            Input({"type": "filter-dropdown", "id": "subject"}, "value"),
            Input({"type": "filter-dropdown", "id": "assessment"}, "value"),
            Input("store-data", "data"),
        ],
    )
    def update_subject(
        cohort_value, subject_value, assessment_value, store_data,
    ):
        if not isinstance(cohort_value, list):
            cohort_value = [cohort_value]

        subject_df = pd.DataFrame.from_records(store_data.get("assessment")).query(
            "(subject==@subject_value) and (cohort.isin(@cohort_value)) and (assessment==@assessment_value)"
        )
        student_id_list = subject_df.student_id.unique()
        student_df = pd.DataFrame.from_records(data.get_students(student_id_list))
        merged_df = pd.merge(
            subject_df, student_df, how="left", left_on="student_id", right_on="_id"
        )
        grade_array = curriculum.subject_scales.get(subject_value)
        figure = {
            "data": [
                go.Scatter(x=merged_df["aps"], y=merged_df["grade"])
            ],
            "layout": go.Layout(
                title=f"{cohort_value}:{subject_value}:{assessment_value}",
                yaxis={
                    "type": "category",
                    "range": [0, len(grade_array)],
                    "categoryorder": "array",
                    "categoryarray": grade_array
                })
        }
        return figure, merged_df.to_dict(orient="records")
