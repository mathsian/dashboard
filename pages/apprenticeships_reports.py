from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_daq as daq
import pandas as pd
from urllib.parse import parse_qs, urlencode
import time
from icecream import ic

from app import app
import app_data

employer_dropdown = dbc.DropdownMenu(
    id={
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "reports",
        "name": "employer"
    },
    nav=True,
)

active_cohort_checkbox = dbc.Checkbox(
    id={
        "type": "checkbox",
        "section": "apprenticeships",
        "page": "reports",
        "name": "active"
    },
    label='Active cohorts only',
    value=1,
    persistence=True,
    persistence_type='memory'
)

active_cohort_tooltip = dbc.Tooltip(
    "An active cohort is one which has at least one continuing learner.",
    target={
        "type": "checkbox",
        "section": "apprenticeships",
        "page": "reports",
        "name": "active"
    }
)

filter_nav = dbc.Nav(
    children=[dbc.Row([dbc.Col(dbc.Label("Employer")), dbc.Col(dbc.NavItem(employer_dropdown))], align='end'),
              dbc.Row([dbc.NavItem(active_cohort_checkbox)]),
              active_cohort_tooltip], vertical=False)

gauge_alltime = daq.Gauge(
    id={
        "type": "gauge",
        "section": "apprenticeships",
        "page": "reports",
        "name": "alltime"
    },
    label="All time attendance",
    labelPosition="bottom",
    scale={
        "start": 0,
        "interval": 5,
        "labelInterval": 4,
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
    size=160,
    style={'margin': '-10px 0px -70px 0px'},
)

gauge_results = daq.Gauge(
    id={
        "type": "gauge",
        "section": "apprenticeships",
        "page": "reports",
        "name": "results"
    },
    label="Average mark",
    labelPosition="bottom",
    scale={
        "start": 0,
        "interval": 10,
        "custom": {40: "Pass", 60: "Merit", 70: "Distinction"}
    },
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
    size=160,
    style={'margin': '-10px 0px -70px 0px'},
)

layout = [
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "reports",
        "name": "learners"
    }, storage_type='memory'),
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "reports",
        "name": "results"
    }, storage_type='memory'),
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "reports",
        "name": "attendance"
    }, storage_type='memory'),
    dbc.Card([
        dbc.CardHeader(html.Center(filter_nav)),
        dbc.CardBody([
            dbc.Row(
                dbc.Col([
                    gauge_alltime,
                    gauge_results])
            )
        ])
    ])
]


@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, "label"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, "children"),
], [
    Input("location", "search"),
], [
    State("location", "pathname"),
    State(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, "label")
])
def update_employers(search, pathname, employer):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of employers
    employers = app_data.get_employer_list()
    employer_query = search_dict.get('employer', False)
    # Default to first employer
    employer = employer or employers[0]
    # If employer in query is valid switch to that
    if employer_query:
        if employer_query[0] in employers:
            employer = employer_query[0]
    employer_items = []
    for c in employers:
        s = urlencode(query={'employer': c})
        employer_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    return employer, employer_items


@app.callback([
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "reports",
            "name": "learners"
        }, 'data'
    ),
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "reports",
            "name": "results"
        }, 'data'
    ),
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "reports",
            "name": "attendance"
        }, 'data'
    )
],

    Input(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, "label"
    ),
    Input(
        {
            "type": "checkbox",
            "section": "apprenticeships",
            "page": "reports",
            "name": "active"
        }, 'value'
    )

)
def update_data(employer, active_cohorts_only):

    if active_cohorts_only:
        selected_cohorts = app_data.get_active_cohorts()
    else:
        selected_cohorts = False

    learners = app_data.get_students_by_employer(employer, selected_cohorts)

    if learners:
        results = app_data.get_student_results_by_employer(employer, selected_cohorts)

        learner_list = ', '.join([f"('{l.get('student_id')}')" for l in learners])

        attendance = app_data.get_apprentice_attendance_by_student_list(learner_list)
    else:
        results = []
        attendance = []
    return learners, results, attendance


@app.callback(
    Output(
        {
            "type": "gauge",
            "section": "apprenticeships",
            "page": "reports",
            "name": "alltime"
        }, 'value'
    ),
    [
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "reports",
                "name": "attendance"
            }, 'data'
        )
    ])
def update_attendance_gauges(attendance):
    if not attendance:
        return 0
    attendance_df = pd.DataFrame(attendance)
    alltime_value = attendance_df["All time attendance (%)"].mean()
    return alltime_value


@app.callback(
    Output(
        {
            "type": "gauge",
            "section": "apprenticeships",
            "page": "reports",
            "name": "results"
        }, 'value'
    ),
    [
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "reports",
                "name": "results"
            }, 'data'
        )
    ])
def update_results_gauge(results):
    if not results:
        return 0
    results_df = pd.DataFrame(results)
    results_value = results_df["mark"].mean()
    return results_value
