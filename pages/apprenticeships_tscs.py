from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_daq as daq
import pandas as pd
from urllib.parse import parse_qs, urlencode
from app import app
import app_data


tsc_dropdown = dbc.DropdownMenu(
    id={
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "tscs",
        "name": "tsc"
    },
    nav=True,
)

filter_nav = dbc.NavItem(tsc_dropdown)

learner_status = html.Div(
    id={
        "type": "div",
        "section": "apprenticeships",
        "page": "tscs",
        "name": "learner_status"
    }
)

gauge_alltime = daq.Gauge(
    id={
        "type": "gauge",
        "section": "apprenticeships",
        "page": "tscs",
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
        "page": "tscs",
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
        "page": "tscs",
        "name": "learners"
    }, storage_type='memory'),
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "tscs",
        "name": "results"
    }, storage_type='memory'),
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "tscs",
        "name": "attendance"
    }, storage_type='memory'),
    dbc.Card([
       dbc.CardHeader(html.Center(filter_nav)),
       dbc.CardBody([
           dbc.Row(
               dbc.Col([
                learner_status,
               ])
           )
       ])
    ])
    ]


@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "tsc"
        }, "label"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "tsc"
        }, "children"),
], [
    Input("location", "search"),
], [
    State("location", "pathname"),
    State(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "tsc"
        }, "label")
])
def update_employers(search, pathname, tsc):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of tscs
    tscs = app_data.get_tsc_list()
    tsc_query = search_dict.get('tsc', False)
    # Default to first tsc
    tsc = tsc or tscs[0]
    # If tsc in query is valid switch to that
    if tsc_query:
        if tsc_query[0] in tscs:
            tsc = tsc_query[0]
    tsc_items = []
    for c in tscs:
        s = urlencode(query={'tsc': c})
        tsc_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    return tsc, tsc_items


@app.callback([
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "learners"
        }, 'data'
    ),
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "results"
        }, 'data'
    ),
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "attendance"
        }, 'data'
    )
],

        Input(
            {
                "type": "dropdown",
                "section": "apprenticeships",
                "page": "tscs",
                "name": "tsc"
            }, "label"
        )

)
def update_data(tsc):
    learners = app_data.get_students_by_tsc(tsc)
    results = app_data.get_student_results_by_tsc(tsc)
    attendance = app_data.get_apprentice_attendance_by_tsc(tsc)
    return learners, results, attendance


@app.callback(
    Output(
        {
            "type": "gauge",
            "section": "apprenticeships",
            "page": "tscs",
            "name": "alltime"
        }, 'value'
    ),
    [
        Input(
            {
                "type": "storage",
                "section": "apprenticeships",
                "page": "tscs",
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
    Output({
        "type": "div",
        "section": "apprenticeships",
        "page": "tscs",
        "name": "learner_status"
    }, 'children'),
    Input({
                "type": "storage",
                "section": "apprenticeships",
                "page": "tscs",
                "name": "learners"
            }, 'data'

    )
)
def update_learner_status(learners):
    if not learners:
        return ""
    learners_df = pd.DataFrame.from_records(learners)
    learner_status = learners_df.groupby('status', observed=False, as_index=False).size().rename(columns={'status': 'Status', 'size': 'Learners'})
    return dbc.Table.from_dataframe(learner_status)


