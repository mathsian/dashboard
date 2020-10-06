import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
team_kudos_table = dash_table.DataTable(
    id="team-kudos-table",
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ] + [{"name": v, "id": v} for v in curriculum.values] + [{"name": "Total", "id": "total"}],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{"column_id": "given_name", "direction": "asc"}],

)
concern_table = dash_table.DataTable(
    id="team-concern-table",
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
        {"name": "Date", "id": "date"},
        {"name": "Category", "id": "category"},
        {"name": "Description", "id": "description"},
        {"name": "Additional", "id": "discrimination"},
        {"name": "Raised by", "id": "from"},],
    style_cell={
                "maxWidth": "240px",
                "textAlign": "left",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
    sort_action="native",
    filter_action="native",
    sort_by=[{"column_id": "date", "direction": "desc"}],

    )
team_attendance_table = dash_table.DataTable(
    id="team-attendance-table",
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{"column_id": "given_name", "direction": "asc"}],
 )
team_kudos_radar = dcc.Graph(id="team-kudos-radar")
content = [
    html.Div(id="content-team-attendance", children=team_attendance_table),
    html.Div(id="content-team-kudos", children=team_kudos_table),
    html.Div(id="content-team-concern", children=concern_table),
]

sidebar = [
    html.Div(id="sidebar-team-attendance"),
    html.Div(id="sidebar-team-kudos", children=team_kudos_radar),
    html.Div(id="sidebar-team-concern"),
]

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
        [
            Output("team-kudos-table", "data"),
            Output("team-concern-table", "data"),
            Output("team-kudos-radar", "figure"),
            ],
        [Input("store-data", "data"),
        Input({"type": "filter-dropdown", "id": "team"}, "value")],
    )
    def update_team_kudos_table(store_data, team_value):
        kudos_data = store_data.get("kudos")
        kudos_df = pd.DataFrame.from_records(kudos_data, columns=["student_id", "date", "ada_value", "description", "points"])
        student_data = store_data.get("student")
        if not team_value:
            student_df = pd.DataFrame.from_records(student_data)
        else:
            student_df = pd.DataFrame.from_records(student_data).query("team==@team_value")
        student_kudos_df = pd.merge(
            student_df, kudos_df, how="left", left_on="_id", right_on="student_id"
        )
        pivot_table_df = pd.pivot_table(
            student_kudos_df,
            values="points",
            index=["student_id", "given_name", "family_name"],
            columns="ada_value",
            aggfunc=sum,
            fill_value=0,
        ).reindex(curriculum.values, axis=1, fill_value=0)
        pivot_table_df["total"] = pivot_table_df.sum(axis=1)
        concern_data = store_data.get("concern")
        concern_df = pd.DataFrame.from_records(concern_data, columns=["student_id", "date", "description", "discrimination", "from", "category"])
        student_concern_df = pd.merge(
            student_df, concern_df, how="inner", left_on="_id", right_on="student_id"
        )

        # add the first value back on the end to make the graph close
        vals = curriculum.values + [curriculum.values[0]]
        fig = make_subplots(specs=[[{"type": "polar"}]])
        fig.add_trace(
            go.Scatterpolar(
                theta=vals,
                r=[pivot_table_df[v].sum() for v in vals],
                subplot="polar"),
            1,1)
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False),
            ))
        # need to reset index otherwise indices are not provided by to_dict
        return (pivot_table_df.reset_index().to_dict(orient="records"),
                student_concern_df.to_dict(orient="records"),
                fig)

    @app.callback(
        [Output("team-attendance-table", "data"), Output("team-attendance-table", "columns")],
        [Input("store-data", "data"), Input({"type": "filter-dropdown", "id": "team"}, "value")])
    def update_team_attendance_table(store_data, team_value):
        attendance_data = store_data.get("attendance")
        attendance_df = pd.DataFrame.from_records(attendance_data)
        ## this is no longer necessary if we only have single selection for teams
        if not isinstance(team_value, list):
            team_value = [team_value]
        student_data = store_data.get("student")
        student_df = pd.DataFrame.from_records(student_data).query("team.isin(@team_value)")
        merged_df = pd.merge(student_df, attendance_df, how="left", left_on="_id", right_on="student_id")
        merged_df['percent_present'] = round(100*merged_df['actual']/merged_df['possible'])
        # merged_pivot = merged_df.pivot(index=["student_id", "given_name", "family_name"], columns="date", values="percent_present").reset_index()
        merged_pivot = merged_df.set_index(["student_id", "given_name", "family_name", "date"])["percent_present"].unstack().reset_index()
        return merged_pivot.to_dict(orient="records"), [{"name": "Given name", "id": "given_name"}, {"name": "Family name", "id": "family_name"}] + [{"name": c, "id": c} for c in merged_pivot.columns[3:]]
