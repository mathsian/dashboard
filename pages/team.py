import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import curriculum
import pandas as pd

subtabnames = ["Attendance", "Kudos", "Concern"]
subtabs = html.Div(
    id="div-subtabs-team",
    children=dcc.Tabs(
        id={"type": "tabs-sub", "id": "team"},
        children=[dcc.Tab(value=f"tab-team-{s.lower()}", label=s) for s in subtabnames],
        value="tab-team-attendance",
    ),
)
kudos_table = dash_table.DataTable(
    id="team-kudos-table",
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ]
    + [{"name": v, "id": v.lower()} for v in curriculum.values],
)
content = [
    html.Div(id="content-team-attendance"),
    html.Div(id="content-team-kudos", children=kudos_table),
    html.Div(id="content-team-concern"),
]
sidebar = [html.Div(id=f"sidebar-team-{s.lower()}") for s in subtabnames]
panel = [html.Div(id=f"panel-team-{s.lower()}") for s in subtabnames]


def register_callbacks(app):
    @app.callback(Output("div-subtabs-team", "hidden"), [Input("tabs-main", "value")])
    def team_hide_subtabs(value):
        return value != "tab-main-team"

    @app.callback(
        [
            Output("content-team-attendance", "hidden"),
            Output("content-team-kudos", "hidden"),
            Output("content-team-concern", "hidden"),
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "team"}, "value"),
        ],
    )
    def team_hide_content(main_value, sub_value):
        if main_value != "tab-main-team":
            return True, True, True
        else:
            return (
                sub_value != "tab-team-attendance",
                sub_value != "tab-team-kudos",
                sub_value != "tab-team-concern",
            )

    @app.callback(
        [
            Output("panel-team-attendance", "hidden"),
            Output("panel-team-kudos", "hidden"),
            Output("panel-team-concern", "hidden"),
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "team"}, "value"),
        ],
    )
    def team_hide_panel(main_value, sub_value):
        if main_value != "tab-main-team":
            return True, True, True
        else:
            return (
                sub_value != "tab-team-attendance",
                sub_value != "tab-team-kudos",
                sub_value != "tab-team-concern",
            )

    @app.callback(
        [
            Output("sidebar-team-attendance", "hidden"),
            Output("sidebar-team-kudos", "hidden"),
            Output("sidebar-team-concern", "hidden"),
        ],
        [
            Input("tabs-main", "value"),
            Input({"type": "tabs-sub", "id": "team"}, "value"),
        ],
    )
    def team_hide_sidebar(main_value, sub_value):
        if main_value != "tab-main-team":
            return True, True, True
        else:
            return (
                sub_value != "tab-team-attendance",
                sub_value != "tab-team-kudos",
                sub_value != "tab-team-concern",
            )

    @app.callback(
        Output("team-kudos-table", "data"),
        [Input("store-data", "data"),],
        [State({"type": "filter-dropdown", "id": "team"}, "value")],
    )
    def update_team_kudos_table(store_data, team_value):
        kudos_data = store_data.get("kudos")
        kudos_df = pd.DataFrame.from_records(kudos_data)
        student_data = store_data.get("student")
        if not isinstance(team_value, list):
            team_value = [team_value]
        student_df = pd.DataFrame.from_records(student_data).query(
            "team.isin(@team_value)"
        )
        student_kudos_df = pd.merge(
            student_df, kudos_df, how="left", left_on="_id", right_on="student_id"
        )
        pivot_table_df = pd.pivot_table(
            student_kudos_df,
            values="points",
            index="_id",
            columns="ada_value",
            aggfunc=sum,
        )
        return pivot_table_df.to_dict(orient="records")
