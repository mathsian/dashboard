import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

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
cohort_attendance_table = dash_table.DataTable(
    id="cohort-attendance-table",
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{"column_id": "given_name", "direction": "asc"}],
)

content = [html.Div(id="content-cohort-summary"),
           html.Div(id="content-cohort-academic"),
           html.Div(id="content-cohort-pastoral", children=cohort_attendance_table)]

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

    @app.callback(
[Output("cohort-attendance-table", "data"),
 Output("cohort-attendance-table", "columns")],
        [
            Input("store-data", "data"),
        ],
    )
    def update_cohort_attendance_table(store_data):
        attendance_data = store_data.get("attendance")
        attendance_df = pd.DataFrame.from_records(attendance_data).sort_values(by="date", ascending=True)
        student_data = store_data.get("student")
        student_df = pd.DataFrame.from_records(student_data)
        merged_df = pd.merge(student_df, attendance_df, how="left", left_on="_id", right_on="student_id")
        merged_df['percent_present'] = round(100*merged_df['actual']/merged_df['possible'])
        merged_pivot = merged_df.set_index(["student_id", "given_name", "family_name", "date"])["percent_present"].unstack().reset_index()
        merged_pivot["change"] = merged_pivot.iloc[:,-1] - merged_pivot.iloc[:,-2]
        table_headings = [
            {"name": "Given name", "id": "given_name"},
            {"name": "Family name", "id": "family_name"}
        ] + [{"name": d, "id": d} for d in merged_pivot.columns[3:-1]] + [{"name": "Change", "id": "change"}]
        table_data = merged_pivot.to_dict(orient='records')
        return table_data, table_headings
