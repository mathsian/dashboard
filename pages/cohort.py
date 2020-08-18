import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

subtabnames = ["Summary", "Academic", "Pastoral"]
subtabs = html.Div(
    id="div-subtabs-cohort",
    children=dcc.Tabs(
        id={"type": "tabs-sub", "id": "cohort"},
        children=[
            dcc.Tab(value=f"tab-cohort-{s.lower()}", label=s) for s in subtabnames
        ],
        value="tab-cohort-summary"
    ),
)

content = [html.Div(id=f"content-cohort-{s.lower()}") for s in subtabnames]
sidebar = [html.Div(id=f"sidebar-cohort-{s.lower()}") for s in subtabnames]

panel = [html.Div(id=f"panel-cohort-{s.lower()}") for s in subtabnames]


def register_callbacks(app):
    @app.callback(Output("div-subtabs-cohort", "hidden"), [Input("tabs-main", "value")])
    def cohort_hide_subtabs(value):
        return value != "tab-main-cohort"

    @app.callback(
        [
            Output("content-cohort-summary", "hidden"),
            Output("content-cohort-academic", "hidden"),
            Output("content-cohort-pastoral", "hidden"),
        ],
        [Input("tabs-main", "value"), Input({"type": "tabs-sub", "id": "cohort"}, "value")],
    )
    def cohort_hide_content(main_value, sub_value):
        if main_value != "tab-main-cohort":
            return True, True, True
        else:
            return (
                sub_value != "tab-cohort-summary",
                sub_value != "tab-cohort-academic",
                sub_value != "tab-cohort-pastoral",
            )

    @app.callback(
        [
            Output("panel-cohort-summary", "hidden"),
            Output("panel-cohort-academic", "hidden"),
            Output("panel-cohort-pastoral", "hidden"),
        ],
        [Input("tabs-main", "value"), Input({"type": "tabs-sub", "id": "cohort"}, "value")],
    )
    def cohort_hide_panel(main_value, sub_value):
        if main_value != "tab-main-cohort":
            return True, True, True
        else:
            return (
                sub_value != "tab-cohort-summary",
                sub_value != "tab-cohort-academic",
                sub_value != "tab-cohort-pastoral",
            )

    @app.callback(
        [
            Output("sidebar-cohort-summary", "hidden"),
            Output("sidebar-cohort-academic", "hidden"),
            Output("sidebar-cohort-pastoral", "hidden"),
        ],
        [Input("tabs-main", "value"), Input({"type": "tabs-sub", "id": "cohort"}, "value")],
    )
    def cohort_hide_sidebar(main_value, sub_value):
        if main_value != "tab-main-cohort":
            return True, True, True
        else:
            return (
                sub_value != "tab-cohort-summary",
                sub_value != "tab-cohort-academic",
                sub_value != "tab-cohort-pastoral",
            )
