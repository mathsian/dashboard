import filters
import dash_tabulator
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

tabs = ["Attendance", "Weekly", "Kudos", "Concern"]
content = [
    dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label=t,
                                        tab_id=f"pastoral-tab-{t.lower()}")
                                for t in tabs
                            ],
                            id=f"pastoral-tabs",
                            card=True,
                            active_tab=f"pastoral-tab-{tabs[0].lower()}",
                        )
                    ],
                    align='end',
                ),
                dbc.Col([filters.cohort]),
                dbc.Col([filters.team])
            ],
                    align='end')
        ],
                       style={"max-height": "10vh"}),
        dbc.CardBody(
            dbc.Row(id=f"pastoral-content", children=[]),
            style={
                "max-height": "70vh",
                "overflow-y": "auto"
            },
        ),
    ])
]
# Attendance tab content
attendance_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "attendance"
    },
    options={
        "resizableColumns": False,
        "layout": "fitData",
        "maxHeight": "60vh",
        "clipboard": "copy"
    },
    theme='bootstrap/tabulator_bootstrap4',
)

gauge_last = daq.Gauge(
    id={
        "type": "gauge",
        "page": "pastoral",
        "tab": "attendance",
        "name": "last_week"
    },
    label="This week",
    scale={
        "start": 0,
        "interval": 10,
        "labelInterval": 2,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
),
gauge_overall = daq.Gauge(
    id={
        "type": "gauge",
        "page": "pastoral",
        "tab": "attendance",
        "name": "overall"
    },
    label="This year",
    scale={
        "start": 0,
        "interval": 10,
        "labelInterval": 2,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
)
# Weekly tab content
weekly_header = html.H4(children=[
    "Week beginning ",
    html.Span(id={
        "type": "text",
        "page": "pastoral",
        "tab": "weekly",
        "name": "wb"
    })
])

weekly_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "weekly"
    },
    options={
        "resizableColumns": False,
        "layout": "fitData",
        "maxHeight": "50vh",
        "clipboard": "copy"
    },
    columns=[
        {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
        },
        {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
        },
        {
            "title": "Present",
            "field": "pr",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        },
        {
            "title": "Authorised",
            "field": "au",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
        {
            "title": "Unauthorised",
            "field": "un",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
        {
            "title": "Late",
            "field": "la",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": ">",
            "headerFilterPlaceholder": "More than",
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
)
weekly_picker = dcc.DatePickerSingle(
    id={
        "type": "picker",
        "page": "pastoral",
        "tab": "weekly"
    },
    date=date.today(),
    display_format="MMM DD YY",
)

# Kudos tab content
kudos_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "kudos",
    },
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "layout": "fitData",
        "maxHeight": "60vh",
        "clipboard": "copy"
    },
    columns=[
        {
            "field": "given_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
        },
        {
            "field": "family_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "search",
        },
    ] + [{
        "title": v[:2],
        "field": v,
        "hozAlign": "right",
        "topCalc": "sum"
    } for v in curriculum.values] + [{
        "title": "Total",
        "field": "total",
        "hozAlign": "right",
        "topCalc": "sum"
    }],
)

fig = make_subplots(specs=[[{"type": "polar"}]])
fig.add_trace(
    go.Scatterpolar(theta=curriculum.values,
                    r=[0 for v in curriculum.values],
                    subplot="polar",
                    fill="toself"), 1, 1)
fig.update_layout(polar=dict(radialaxis=dict(visible=False)), height=300)

kudos_radar = dcc.Graph(id={
    "type": "graph",
    "page": "pastoral",
    "tab": "kudos",
},
                        config={"displayModeBar": False},
                        figure=fig)

# Concern tab content
concern_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
    },
    columns=[
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Email",
            "field": "student_email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Date",
            "field": "date",
            "width": "10%"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Category",
            "field": "category",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_categories
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Stage",
            "field": "stage",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_stages
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Description",
            "field": "description",
            # "formatter": "plaintext",
            "width": "20%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Raised by",
            "field": "from",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Additional",
            "field": "discrimination",
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_discrimination
            },
            "headerFilterPlaceholder": "filter",
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "layout": "fitData",
        "maxHeight": "60vh",
        "clipboard": "copy"
    },
)

# Validation layout contains everything needed to validate all callbacks
validation_layout = content + [
    attendance_table, gauge_last, gauge_overall, weekly_header, weekly_table,
    weekly_picker, kudos_table, kudos_radar, concern_table
]
# Associate each tab with its content
tab_map = {
    "pastoral-tab-attendance": [
        dbc.Col(gauge_overall, width=2),
        dbc.Col(gauge_last),
        dbc.Col(attendance_table)
    ],
    "pastoral-tab-weekly":
    dbc.Col([
        dbc.Row(children=[
            dbc.Col(width=3, children=weekly_picker),
            dbc.Col(weekly_header)
        ],
                style={"max-height": "10vh"}),
        dbc.Row(dbc.Col(weekly_table)),
    ]),
    "pastoral-tab-kudos": [
        dbc.Col(width=4, children=[kudos_radar]),
        dbc.Col(width=8, children=[kudos_table])
    ],
    "pastoral-tab-concern": [
        dbc.Col(width=12, children=concern_table),
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
                "type": "gauge",
                "page": "pastoral",
                "tab": "attendance",
                "name": "last_week",
            }, "value"),
        Output(
            {
                "type": "gauge",
                "page": "pastoral",
                "tab": "attendance",
                "name": "overall",
            }, "value"),
    ],
    [
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
    ],
)
def update_pastoral_attendance(filter_value):
    cohort, team = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], [], 0, 0
    student_ids = [s.get('_id') for s in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    if not attendance_docs:
        return [], [], 0, 0
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        'date > @this_year_start')
    weekly_df = attendance_df.query("subtype == 'weekly'")
    last_week_date = weekly_df["date"].max()
    overall_totals = weekly_df.sum()
    last_week_totals = weekly_df.query("date == @last_week_date").sum()
    overall_percent = round(
        100 * overall_totals['actual'] / overall_totals['possible'], 1)
    last_week_percent = round(
        100 * last_week_totals['actual'] / last_week_totals['possible'], 1)
    # Merge on student id
    merged_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                         weekly_df,
                         left_on='_id',
                         right_on='student_id',
                         how='left')
    # Get per student totals
    cumulative_df = merged_df.groupby("student_id").sum().reset_index()
    cumulative_df['cumulative_percent_present'] = round(
        100 * cumulative_df['actual'] / cumulative_df['possible'])
    # Calculate percent present
    merged_df['percent_present'] = round(100 * merged_df['actual'] /
                                         merged_df['possible'])
    # Pivot to bring dates to columns
    attendance_pivot = merged_df.set_index(
        ["student_id", "given_name", "family_name",
         "date"])["percent_present"].unstack().reset_index()
    # Add the cumulative column
    attendance_pivot = pd.merge(
        attendance_pivot,
        cumulative_df[["student_id", "cumulative_percent_present"]],
        how='left',
        left_on="student_id",
        right_on="student_id",
        suffixes=("", "_y"))
    columns = [
        {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
        },
        {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
        },
    ]
    columns.extend([
        {
            #"name": data.format_date(d),
            "title": d,
            "field": d,
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        } for d in attendance_pivot.columns[-2:-1]
    ])
    columns.append({
        "title": "Year",
        "field": "cumulative_percent_present",
        "hozAlign": "right",
        "headerFilter": True,
        "headerFilterFunc": "<",
        "headerFilterPlaceholder": "Less than",
    })

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
    cohort, team = filter_value
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
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
    }, "data"),
    [Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value")],
)
def update_pastoral_concern(filter_value):
    # Get list of relevant students
    cohort, team = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return []
    student_ids = [s.get('_id') for s in enrolment_docs]
    # Build concern dataframe
    concern_docs = data.get_data("concern", "student_id", student_ids)
    if not concern_docs:
        return []
    concern_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                          pd.DataFrame.from_records(concern_docs),
                          how="right",
                          left_on="_id",
                          right_on="student_id").sort_values("date",
                                                             ascending=False)
    return concern_df.to_dict(orient="records")


@app.callback([
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "weekly"
    }, "data"),
    Output({
        "type": "text",
        "page": "pastoral",
        "tab": "weekly",
        "name": "wb"
    }, "children"),
], [
    Input({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value"),
    Input({
        "type": "picker",
        "page": "pastoral",
        "tab": "weekly"
    }, "date")
])
def update_weekly_table(filter_value, picker_value):
    # Get list of relevant students
    cohort, team = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], ""
    student_ids = [s.get('_id') for s in enrolment_docs]
    enrolment_df = pd.DataFrame.from_records(enrolment_docs)
    # Get attendance for the latest week before the chosen date
    attendance_df = pd.DataFrame.from_records(
        data.get_data("attendance", "student_id",
                      student_ids)).query("subtype == 'weekly'").query(
                          "date <= @picker_value").query("date == date.max()")
    # Picked too early a date?
    if attendance_df.empty:
        attendance_df = pd.DataFrame.from_records(
            data.get_data("attendance", "student_id",
                          student_ids)).query("date == date.min()")
    attendance_df.eval("pr = 100*actual/possible", inplace=True)
    attendance_df.eval("un = 100*unauthorised/possible", inplace=True)
    attendance_df.eval("au = 100*authorised/possible", inplace=True)
    attendance_df.eval("la = 100*late/actual", inplace=True)
    merged_df = pd.DataFrame.merge(enrolment_df,
                                   attendance_df.round(),
                                   how='left',
                                   left_on='_id',
                                   right_on='student_id')
    return merged_df.to_dict(orient='records'), data.format_date(
        attendance_df["date"].iloc[0])


@app.callback(
    [
        Output({
            "type": "filter-dropdown",
            "filter": "team"
        }, "options"),
        Output({
            "type": "filter-dropdown",
            "filter": "team"
        }, "value"),
    ],
    [Input({
        "type": "filter-dropdown",
        "filter": "cohort"
    }, "value")],
)
def update_subject_filter(cohort_value):
    teams = data.get_teams(cohort_value)
    return [
        [{
            "label": t,
            "value": t
        } for t in teams],
        None,
    ]
