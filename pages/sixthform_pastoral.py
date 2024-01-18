from urllib.parse import parse_qs, urlencode
import dash
from app import app
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data
import curriculum

cohort_dropdown = dbc.DropdownMenu(id="cohort-dropdown",
                                   nav=True,)
team_dropdown = dbc.DropdownMenu(id="team-dropdown", nav=True)

kudos_switch = dbc.Form(
[
    dbc.Label("Kudos this"),
    dbc.Select(
        options=[
            {"label": "academic year", "value": "y"},
            {"label": "term", "value": "t"},
            {"label": "half term", "value": "h"},
        ],
        value="t",
        id="kudos-switch",
    )
])

fig = make_subplots(specs=[[{"type": "polar"}]])
fig.add_trace(
    go.Scatterpolar(theta=curriculum.values,
                    r=[0 for v in curriculum.values],
                    subplot="polar",
                    fill="toself"), 1, 1)
fig.update_layout(polar=dict(radialaxis=dict(visible=False)), height=300,
                  # title={'text': 'Kudos this year', 'x': 0, 'y': 0, 'xanchor': 'right', 'yanchor': 'bottom'},
                  margin={'t': 16},
                  title_font={'family': 'Titillium'})

kudos_radar = dcc.Graph(id={
    "type": "graph",
    "section": "sixthform",
    "page": "pastoral",
    "name": "kudos",
},
                        config={"displayModeBar": False},
                        figure=fig,
    style={'margin': '-10px 0px -70px 0px'},
)

gauge_overall = daq.Gauge(
    id={
        "type": "gauge",
        "section": "sixthform",
        "page": "pastoral",
        "name": "year"
    },
    label="Attendance this year",
    scale={
        "start": 0,
        "interval": 10,
        "labelInterval": 2,
    },
    size=180,
    showCurrentValue=True,
    units="%",
    value=0,
    min=0,
    max=100,
    style={'margin': '-10px 0px -70px 0px'},
)

filter_nav = dbc.Nav([
    dbc.NavItem(cohort_dropdown),
    dbc.NavItem(team_dropdown)
],
                            fill=True)


layout =[
    dcc.Store(id="sixthform-pastoral-store", storage_type='memory'),
    html.Center([
        dbc.Card([
            dbc.CardHeader(filter_nav),
            dbc.CardBody(gauge_overall)
        ]),
        dbc.Card([
            dbc.CardHeader(kudos_switch),
            dbc.CardBody(dcc.Loading(kudos_radar))
        ])
    ]),
    ]


@app.callback([
    Output("cohort-dropdown", "label"),
    Output("cohort-dropdown", "children"),
    Output("team-dropdown", "label"),
    Output("team-dropdown", "children"),
    Output("sixthform-pastoral-store", "data")
], [
    Input("location", "pathname"),
    Input("location", "search"),
    Input("kudos-switch", "value"),
], [State("team-dropdown", "label"),
    State("cohort-dropdown", "label"),
    State("sixthform-pastoral-store", "data")])
def update_teams(pathname, search, kudos_switch_value, team, cohort, store_data):
    current_team = team
    current_cohort = cohort

    # Set teams and cohort from location
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', [curriculum.cohorts[-1]])[0]
    teams = data.get_teams(cohort)
    # Get list of teams
    team = search_dict.get("team", ['All'])[0]
    # Populate the dropdowns
    team_items = [dbc.DropdownMenuItem()]
    for t in ['All'] + teams:
        s = urlencode(query={'cohort': cohort, 'team': t})
        team_items.append(dbc.DropdownMenuItem(t, href=f'{pathname}?{s}'))
    cohort_items = []
    for c in curriculum.cohorts:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    # If the team and cohort both haven't changed then no need to update data unless the kudos date has changed
    if team == current_team and cohort == current_cohort and dash.callback_context.triggered_id != 'kudos-switch':
        return cohort, cohort_items, team, team_items, dash.no_update
    # Get data in scope
    term_date = data.get_term_date_from_rems()

    enrolment_docs = data.get_enrolment_by_cohort_team(cohort, team)
    student_ids = [e.get('_id') for e in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    # assessment_docs = data.get_data("assessment", "student_id", student_ids)
    # Kudos processing
    kudos_docs = data.get_data("kudos", "student_id", student_ids)

    if kudos_switch_value == 'y':
        kudos_start = term_date['year_start']
    elif kudos_switch_value == 't':
        kudos_start = term_date['term_start']
    elif kudos_switch_value == 'h':
        kudos_start = term_date['half_term_start']

    kudos_df = pd.merge(pd.DataFrame.from_records(enrolment_docs,
                                                  columns=['_id', 'given_name', 'family_name']),
                        pd.DataFrame.from_records(kudos_docs,
                                                  columns=['student_id', 'ada_value', 'date', 'from', 'points']).query("date >= @kudos_start"),
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
    kudos_pivot_docs = kudos_pivot_df.sort_values('total', ascending=False).to_dict(orient='records')

    note_docs = data.get_data("note", "student_id", student_ids)
    store_data = {
        "student_ids": student_ids,
        "enrolment_docs": enrolment_docs,
        "attendance_docs": attendance_docs,
        # "assessment_docs": assessment_docs,
        "kudos_docs": kudos_docs,
        "kudos_pivot_docs": kudos_pivot_docs,
        "note_docs": note_docs,
        "term_date": term_date
    }
    return (cohort, cohort_items, team, team_items, store_data)


@app.callback(
    Output({
        "type": "graph",
        "section": "sixthform",
        "page": "pastoral",
        "name": "kudos",
    }, "figure"), [Input("sixthform-pastoral-store", "data")], [
        State({
            "type": "graph",
            "section": "sixthform",
            "page": "pastoral",
            "name": "kudos",
        }, "figure")
    ])
def update_kudos_radar(store_data, current_figure):
    kudos_pivot_docs = store_data.get('kudos_pivot_docs')
    if not kudos_pivot_docs:
        current_figure["data"][0]["r"] = [0 for v in curriculum.values]
        return current_figure
    kudos_pivot_df = pd.DataFrame.from_records(kudos_pivot_docs)
    r = [kudos_pivot_df[v].sum() for v in curriculum.values]
    current_figure["data"][0]["r"] = r
    return current_figure


@app.callback(
Output(
{
        "type": "gauge",
        "section": "sixthform",
        "page": "pastoral",
        "name": "year"
    }, "value"
),
   [
        Input("sixthform-pastoral-store", "data")
    ]
)
def update_year_gauge(store_data):
    attendance_docs = store_data.get('attendance_docs')
    term_date = store_data.get('term_date')
    if not attendance_docs:
        return 0
    this_year_start = term_date['year_start']
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        'date > @this_year_start')
    weekly_df = attendance_df.query("subtype == 'weekly'")
    # last_week_date = weekly_df["date"].max()
    overall_totals = weekly_df.sum()
    # last_week_totals = weekly_df.query("date == @last_week_date").sum()
    overall_percent = round(
        100 * overall_totals['actual'] / overall_totals['possible'], 1)
    # last_week_percent = round(
    #     100 * last_week_totals['actual'] / last_week_totals['possible'], 1)
    return overall_percent
