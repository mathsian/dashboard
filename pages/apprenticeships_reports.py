import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq
import pandas as pd
from urllib.parse import parse_qs, urlencode
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

cohort_dropdown = dbc.DropdownMenu(
    id={
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "reports",
        "name": "cohort"
    },
    nav=True,
)

filter_nav = dbc.Form([
    dbc.Row([
        dbc.Col([
            dbc.Label("Employer"), dbc.NavItem(employer_dropdown)
            ]),
        dbc.Col([
            dbc.Label("Cohort"), dbc.NavItem(cohort_dropdown)
        ])
    ]),


])

gauge_alltime = daq.Gauge(
    id={
        "type": "gauge",
        "section": "apprenticeships",
        "page": "reports",
        "name": "alltime"
    },
    label="All time attendance (continuing learners)",
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
    size=170,
    style={'margin-bottom': -60},
)

# gauge_ninety = daq.Gauge(
#     id={
#         "type": "gauge",
#         "section": "apprenticeships",
#         "page": "reports",
#         "name": "ninety"
#     },
#     label="90 day",
#     labelPosition="top",
#     scale={
#         "start": 0,
#         "interval": 5,
#         "labelInterval": 4,
#     },
#     showCurrentValue=True,
#     units="%",
#     value=0,
#     min=0,
#     max=100,
#     size=170,
# )

gauge_results = daq.Gauge(
    id={
        "type": "gauge",
        "section": "apprenticeships",
        "page": "reports",
        "name": "results"
    },
    label="Average mark (continuing learners)",
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
    size=170,
)

layout = [
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
    dbc.Row(dbc.Col(filter_nav)),
    dbc.Row(dbc.Col([
        gauge_alltime,
        gauge_results
    ]))
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
    return (employer, employer_items)


@app.callback([
    Output(
{
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "cohort"
        }, "label"
    ),
    Output(
{
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "cohort"
        }, "children"
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
[
    Input(
{
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "employer"
        }, "label"
    )
],
[
State(
{
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "reports",
            "name": "cohort"
        }, "label"
    ),
    State(
        "location", "search"
    ),
    State(
        "location", "pathname"
    )
])
def update_cohorts(employer, cohort, search, pathname):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts
    cohorts = ['All'] + app_data.get_cohorts_by_employer(employer)
    cohort_query = search_dict.get('cohort', False)
    # If current cohort is valid for employer, default to that
    # Else first cohort
    cohort = cohort if cohort in cohorts else cohorts[0]
    # If cohort in query is valid switch to that
    if cohort_query:
        if cohort_query[0] in cohorts:
            cohort = cohort_query[0]
    cohort_items = []
    for c in cohorts:
        s = urlencode(query={'employer': employer, 'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    results = app_data.get_student_results_by_employer_cohort(employer, cohort)
    attendance = app_data.get_apprentice_attendance_by_employer_cohort(employer, cohort)
    return (cohort, cohort_items, results, attendance)


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
    results_df = pd.DataFrame(results).query('status == "Continuing"')
    results_value = results_df["mark"].mean()
    return results_value
