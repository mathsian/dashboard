import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd

from app import app
import data

name = "pastoral"
tabs = ["Attendance", "Kudos", "Concern"]
content = [
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=t, tab_id=f"{name}-tab-{t.lower()}")
                    for t in tabs
                ],
                id=f"{name}-tabs",
                card=True,
                active_tab=f"{name}-tab-{tabs[0].lower()}",
            )),
        dbc.CardBody(
            dbc.Row([
                dbc.Col(width=3, children=html.Div(id=f"{name}-sidebar")),
                dbc.Col(width=7, children=html.Div(id=f"{name}-main")),
                dbc.Col(width=2, children=html.Div(id=f"{name}-panel")),
            ])),
    ])
]

attendance_table = dash_table.DataTable(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "attendance"
    },
    columns=[
        {
            "name": "Given name",
            "id": "given_name"
        },
        {
            "name": "Family name",
            "id": "family_name"
        },
    ],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{
        "column_id": "given_name",
        "direction": "asc"
    }],
)


@app.callback(
    [
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "attendance"
        }, "columns"),
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "attendance"
        }, "data"),
    ],
    [
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
    ],
)
def update_attendance_table(filter_value):
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], []
    student_ids = [s.get('_id') for s in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    # Merge on student id
    attendance_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                             pd.DataFrame.from_records(attendance_docs),
                             left_on='_id',
                             right_on='student_id',
                             how='left')
    # Calculate percent present
    attendance_df['percent_present'] = round(100 * attendance_df['actual'] /
                                             attendance_df['possible'])
    # Pivot to bring dates to columns
    attendance_pivot = attendance_df.set_index(["student_id", "given_name", "family_name", "date"])["percent_present"].unstack().reset_index()
    columns = [
        {
            "name": "Given name",
            "id": "given_name"
        },
        {
            "name": "Family name",
            "id": "family_name"
        },
    ] + [{"name": data.format_date(d), "id": d} for d in attendance_pivot.columns[-4:]]
    return columns, attendance_pivot.to_dict(orient='records')


@app.callback(
    [
        Output(f"{name}-sidebar", "children"),
        Output(f"{name}-main", "children"),
        Output(f"{name}-panel", "children"),
    ],
    [
        Input(f"{name}-tabs", "active_tab"),
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
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
