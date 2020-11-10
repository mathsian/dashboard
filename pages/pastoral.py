import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table

from app import app
import data

name = "pastoral"
tabs = ["Attendance", "Kudos", "Concern"]
content = [
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [dbc.Tab(label=t, tab_id=f"{name}-tab-{t.lower()}") for t in tabs],
                    id=f"{name}-tabs",
                    card=True,
                    active_tab=f"{name}-tab-{tabs[0].lower()}",
                )
            ),
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(width=3, children=html.Div(id=f"{name}-sidebar")),
                        dbc.Col(width=7, children=html.Div(id=f"{name}-main")),
                        dbc.Col(width=2, children=html.Div(id=f"{name}-panel")),
                    ]
                )
            ),
        ]
    )
]

attendance_table = dash_table.DataTable(
    id={"type": "table", "page": "pastoral", "tab": "attendance"},
    columns=[
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{"column_id": "given_name", "direction": "asc"}],
)


@app.callback(
    [
        Output({"type": "table", "page": "pastoral", "tab": "attendance"}, "columns"),
        Output({"type": "table", "page": "pastoral", "tab": "attendance"}, "data"),
    ],
    [Input({"type": "filter-dropdown", "filter": ALL}, "value"),],
)
def update_attendance_table(filter_value):
    print(filter_value)
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team", (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], []
    columns = [
        {"name": "Given name", "id": "given_name"},
        {"name": "Family name", "id": "family_name"},
    ]
    print(enrolment_docs)
    return columns, enrolment_docs


@app.callback(
    [
        Output(f"{name}-sidebar", "children"),
        Output(f"{name}-main", "children"),
        Output(f"{name}-panel", "children"),
    ],
    [
        Input(f"{name}-tabs", "active_tab"),
        Input({"type": "filter-dropdown", "filter": ALL}, "value"),
        Input("store-data", "data"),
    ],
)
def get_content(active_tab, filter_value, store_data):
    return [
        get_sidebar(active_tab, filter_value, store_data),
        get_main(active_tab, filter_value, store_data),
        get_panel(active_tab, filter_value, store_data),
    ]


def get_sidebar(active_tab, filter_value, store_data):
    return f"{name} {active_tab} sidebar"


def get_main(active_tab, filter_value, store_data):
    if active_tab == "pastoral-tab-attendance":
        return attendance_table
    else:
        return f"{name} {active_tab} {filter_value} {store_data}"


def get_panel(active_tab, filter_value, store_data):
    return f"{name} {active_tab} panel"
