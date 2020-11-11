import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import app
import data
import curriculum

tabs = ["Attendance", "Kudos", "Concern"]
content = [
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=t, tab_id=f"pastoral-tab-{t.lower()}")
                    for t in tabs
                ],
                id=f"pastoral-tabs",
                card=True,
                active_tab=f"pastoral-tab-{tabs[0].lower()}",
            )),
        dbc.CardBody(dbc.Row(id=f"pastoral-content", children=[])),
    ])
]
# Attendance tab content
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
attendance_summary = html.Div(children=[
    html.H6("Last week"),
    html.P(
        id={
            "type": "text",
            "page": "pastoral",
            "tab": "attendance",
            "name": "last_week"
        }),
    html.H6("Overall"),
    html.P(id={
        "type": "text",
        "page": "pastoral",
        "tab": "attendance",
        "name": "overall"
    }),
])

# Kudos tab content
kudos_table = dash_table.DataTable(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "kudos",
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
    ] + [{
        "name": v[:2],
        "id": v
    } for v in curriculum.values] + [{
        "name": "Total",
        "id": "total"
    }],
    style_cell={"textAlign": "left"},
    sort_action="native",
    filter_action="native",
    sort_by=[{
        "column_id": "given_name",
        "direction": "asc"
    }],
)

fig = make_subplots(specs=[[{"type": "polar"}]])
fig.add_trace(
    go.Scatterpolar(theta=curriculum.values,
                    r=[0 for v in curriculum.values],
                    subplot="polar",
                    fill="toself"), 1, 1)
fig.update_layout(polar=dict(radialaxis=dict(visible=False), ))

kudos_radar = dcc.Graph(id={
    "type": "graph",
    "page": "pastoral",
    "tab": "kudos",
},
                        config={"displayModeBar": False},
                        figure=fig)

# Concern tab content
concern_table = dash_table.DataTable(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
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
        {
            "name": "Date",
            "id": "date"
        },
        {
            "name": "Category",
            "id": "category"
        },
        {
            "name": "Description",
            "id": "description"
        },
        {
            "name": "Additional",
            "id": "discrimination"
        },
        {
            "name": "Raised by",
            "id": "from"
        },
    ],
    sort_action="native",
    filter_action="native",
    sort_by=[{
        "column_id": "date",
        "direction": "desc"
    }],
    style_cell={
        "textAlign": "left",
        "maxWidth": 100,
    },
    style_cell_conditional=[{
        "if": {
            "column_id": "description"
        },
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }],
)

# Validation layout contains everything needed to validate all callbacks
validation_layout = content + [
    attendance_table, attendance_summary, kudos_table, kudos_radar,
    concern_table
]
# Associate each tab with its content
tab_map = {
    "pastoral-tab-attendance":
    [
            dbc.Col(width=8, children=attendance_table),
            dbc.Col(children=attendance_summary)
        ],
    "pastoral-tab-kudos":
[
            dbc.Col(width=8, children=kudos_table),
            dbc.Col(children=kudos_radar)
        ],
    "pastoral-tab-concern":
[
            dbc.Col(width=10, children=concern_table),
        ],
}


@app.callback(
    Output(f"pastoral-content", "children"),
    [
        Input(f"pastoral-tabs", "active_tab"),
    ],
)
def get_content(active_tab):
    return tab_map.get(active_tab)


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
        Output(
            {
                "type": "text",
                "page": "pastoral",
                "tab": "attendance",
                "name": "last_week",
            }, "children"),
        Output(
            {
                "type": "text",
                "page": "pastoral",
                "tab": "attendance",
                "name": "overall",
            }, "children"),
    ],
    [
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
    ],
)
def update_pastoral_attendance(filter_value):
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], [], "", ""
    student_ids = [s.get('_id') for s in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    attendance_df = pd.DataFrame.from_records(attendance_docs)
    last_week_date = attendance_df["date"].max()
    overall_totals = attendance_df.sum()
    last_week_totals = attendance_df.query("date == @last_week_date").sum()
    overall_percent = round(100 * overall_totals['actual'] /
                            overall_totals['possible'])
    last_week_percent = round(100 * last_week_totals['actual'] /
                              last_week_totals['possible'])
    # Merge on student id
    attendance_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                             attendance_df,
                             left_on='_id',
                             right_on='student_id',
                             how='left')
    # Calculate percent present
    attendance_df['percent_present'] = round(100 * attendance_df['actual'] /
                                             attendance_df['possible'])
    # Pivot to bring dates to columns
    attendance_pivot = attendance_df.set_index(
        ["student_id", "given_name", "family_name",
         "date"])["percent_present"].unstack().reset_index()
    columns = [
        {
            "name": "Given name",
            "id": "given_name"
        },
        {
            "name": "Family name",
            "id": "family_name"
        },
    ] + [{
        "name": data.format_date(d),
        "id": d
    } for d in attendance_pivot.columns[-4:]]
    return columns, attendance_pivot.to_dict(
        orient='records'), last_week_percent, overall_percent


@app.callback(
    [
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "kudos",
        }, "data"),
        Output({
            "type": "graph",
            "page": "pastoral",
            "tab": "kudos",
        }, "figure")
    ], [Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value")],
    [State({
        "type": "graph",
        "page": "pastoral",
        "tab": "kudos",
    }, "figure")])
def update_pastoral_kudos(filter_value, current_figure):
    # Get list of relevant students
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], current_figure
    student_ids = [s.get('_id') for s in enrolment_docs]
    # Build kudos dataframe
    kudos_docs = data.get_data("kudos", "student_id", student_ids)
    if not kudos_docs:
        current_figure["data"][0]["r"] = [0 for v in curriculum.values]
        return [], current_figure
    kudos_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                        pd.DataFrame.from_records(kudos_docs),
                        how="left",
                        left_on="_id",
                        right_on="student_id")
    kudos_pivot_df = pd.pivot_table(
        kudos_df,
        values="points",
        index=["student_id", "given_name", "family_name"],
        columns="ada_value",
        aggfunc=sum,
        fill_value=0,
    ).reindex(curriculum.values, axis=1, fill_value=0)
    kudos_pivot_df["total"] = kudos_pivot_df.sum(axis=1)
    kudos_pivot_df = kudos_pivot_df.reset_index()
    r = [kudos_pivot_df[v].sum() for v in curriculum.values]
    current_figure["data"][0]["r"] = r
    return kudos_pivot_df.to_dict(orient='records'), current_figure


@app.callback(
    [
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "concern",
        }, "data"),
        Output({
            "type": "table",
            "page": "pastoral",
            "tab": "concern",
        }, "tooltip_data"),
    ],
    [Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value")],
)
def update_pastoral_concern(filter_value):
    # Get list of relevant students
    cohort, team, _ = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return []
    student_ids = [s.get('_id') for s in enrolment_docs]
    # Build kudos dataframe
    concern_docs = data.get_data("concern", "student_id", student_ids)
    if not concern_docs:
        return []
    concern_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                          pd.DataFrame.from_records(concern_docs),
                          how="right",
                          left_on="_id",
                          right_on="student_id").sort_values("date", ascending=False)
    tooltips = [{"description": d} for d in concern_df["description"].tolist()]
    return concern_df.to_dict(orient="records"), tooltips
