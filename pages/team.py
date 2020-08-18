import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

subtabnames = ["Attendance", "Kudos", "Concern"]
subtabs = html.Div(
    id="div-subtabs-team",
    children=dcc.Tabs(
        id={"type": "tabs-sub", "id": "team"},
        children=[dcc.Tab(value=f"tab-team-{s.lower()}", label=s) for s in subtabnames],
        value="tab-team-attendance",
    ),
)
content = [html.Div(id=f"content-team-{s.lower()}") for s in subtabnames]
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
