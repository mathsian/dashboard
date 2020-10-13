"""
Layout for student-focused data
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from pages import report
from forms import kudos, concern
import pandas as pd
import curriculum
import plotly.graph_objects as go
import data

subtabs = html.Div(
    id="div-subtabs-student",
    children=dcc.Tabs(
        id={"type": "tabs-sub", "id": "student"},
        children=[
            dcc.Tab(value="tab-student-report", label="Report"),
            dcc.Tab(value="tab-student-kudos", label="Kudos"),
            dcc.Tab(value="tab-student-concern", label="Concern"),
        ],
        value="tab-student-report",
    ),
)

student_list = (
    dash_table.DataTable(
        id="sidebar-student-table",
        columns=[
            {"name": "Given Name", "id": "given_name"},
            {"name": "Family Name", "id": "family_name"},
        ],
        style_cell={"textAlign": "left"},
        row_selectable="multi",
        sort_action="native",
        filter_action="native",
        sort_by=[{"column_id": "given_name", "direction": "asc"}],
        fixed_rows={"headers": True},
        style_table={"height": '350px',
                     "minWidth": "100%"},
    ),
)

content = [
    html.Div(id="content-student-report", children=report.layout,),
    html.Div(id="content-student-kudos", children=kudos.layout,),
    html.Div(id="content-student-concern", children=concern.layout,),
]
sidebar = [
    html.Div(id="sidebar-student", children=student_list,),
]
panel = [html.Div()]


def register_callbacks(app):
    @app.callback(
        Output("div-subtabs-student", "hidden"), [Input("tabs-main", "value")]
    )
    def student_hide_subtabs(value):
        return value != "tab-main-student"

    @app.callback(
        [
            Output("content-student-report", "hidden"),
            Output("content-student-kudos", "hidden"),
            Output("content-student-concern", "hidden"),
            Output("sidebar-student", "hidden"),
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "student"}, "value"),
        ],
    )
    def student_hide_content(main_value, sub_value):
        if main_value != "tab-main-student":
            return True, True, True, True
        else:
            return (
                sub_value != "tab-student-report",
                sub_value != "tab-student-kudos",
                sub_value != "tab-student-concern",
                False,
            )

    @app.callback(
        [
            Output("report-heading", "children"),
            Output("report-subheading", "children"),
            Output("report-attendance", "children"),
            Output("report-academic", "children"),
            Output("report-kudos", "data"),
            Output("report-concerns", "data"),
        ],
        [Input("store-student", "data")],
        [
            State("store-data", "data"),
        ],
    )
    def generate_report(
        store_student,
        store_data,
    ):
        if not store_student:
            return "Select a student from the list", "", "", "", [], []
        report_student = store_student[-1]
        student_id = report_student.get("_id")
        heading_layout = (
            f"{report_student.get('given_name')} {report_student.get('family_name')}"
        )
        # Assessment
        assessment_df = pd.DataFrame.from_records(store_data.get("assessment"), columns=["subtype", "subject", "student_id", "cohort", "assessment", "grade", "comment", "date"]).query(
            f'student_id=="{student_id}"'
        )
        assessment_layout = []
        # For each subject, graph grades against time
        for sbj in assessment_df["subject"].unique():
            results = assessment_df.query(f'subject == "{sbj}"').sort_values(
                by="date"
            )
            for result in results.to_dict(orient='records'):
                assessment_layout.append(html.H6(result.get("subject")))
                assessment_layout.append(html.P(f"{result.get('date')}: {result.get('grade')}"))
                assessment_layout.append(html.P(result.get('comment')))
        # Kudos
        kudos_df = pd.DataFrame.from_records(store_data.get('kudos'), columns=["student_id", "date", "ada_value", "description", "points", "from"]).query(
            f'student_id=="{student_id}"'
        )
        kudos_df["date"] = kudos_df["date"].apply(lambda d: data.format_date(d))
        kudos_data = kudos_df.to_dict(orient="records")

        # Concerns
        concerns_df = pd.DataFrame.from_records(store_data.get('concern'), columns=["student_id", "date", "category", "discrimination", "description", "from"]).query(
            f'student_id=="{student_id}"'
        )
        concerns_df["date"] = concerns_df["date"].apply(lambda d: data.format_date(d))
        concerns_data = concerns_df.to_dict(orient="records")

        # Attendance
        attendance_df = pd.DataFrame.from_records(store_data.get('attendance')).query(f'student_id==@student_id')
        attendance_df['percent'] = 100*attendance_df['actual']/attendance_df['possible']
        figure = go.Figure()
        figure.add_trace(
            go.Bar(
                x=attendance_df["date"],
                y=attendance_df["percent"],
                name="Weekly attendance"
            ))
        figure.add_trace(
go.Scatter(
    x=attendance_df["date"],
    y=[95]*len(attendance_df),
    name="Target attendance",
    line={"color": "green", "dash": "dot"}
)
        )
        attendance_graph = dcc.Graph(
            figure = figure,
            config={
                "displayModeBar": False
            }
        )

        return heading_layout, "", attendance_graph, assessment_layout, kudos_data, concerns_data

    @app.callback(
        [Output("sidebar-student-table", "data"),
         Output("sidebar-student-table", "selected_rows")],
        [Input("store-data", "data"), Input({"type": "filter-dropdown", "id": "team"}, "value")],
    )
    def update_sidebar_student_table(store_data, team_value):
        student_df = pd.DataFrame.from_records(store_data.get('student')).rename(
            columns={"_id": "id"}
        )
        if team_value:
            if isinstance(team_value, list):
                student_df = student_df[student_df.team.isin(team_value)]
            else:
                student_df = student_df[student_df.team == team_value]
        return student_df.to_dict(orient="records"), []

def subject_assessment_graph():
    subtype = results.iloc[0].subtype
    grade_array = curriculum.scales[subtype]
    assessment_layout.append(
        dcc.Graph(
            figure={
                "data": [go.Scatter(x=results["date"], y=results["grade"])],
                "layout": go.Layout(
                    title=sbj,
                    yaxis={
                        "type": "category",
                        "range": [0, len(grade_array)],
                        "categoryorder": "array",
                        "categoryarray": grade_array,
                    },
                ),
            }
        )
    )
