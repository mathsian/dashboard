from urllib.parse import parse_qs, urlencode
import dash
from app import app
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import data

cohort_dropdown = dbc.DropdownMenu(id="cohort-dropdown", nav=True, bs_size='sm')
team_dropdown = dbc.DropdownMenu(id="team-dropdown", nav=True, bs_size='sm')

cardheader_layout = dbc.Nav(
    [
        dcc.Store(id="sixthform-pastoral", storage_type='memory'),
        dbc.NavItem(cohort_dropdown),
        dbc.NavItem(team_dropdown)
    ], card=True
)

sidebar_layout = html.Div("SF pastoral sidebar")


@app.callback([
    Output("cohort-dropdown", "label"),
    Output("cohort-dropdown", "children"),
    Output("team-dropdown", "label"),
    Output("team-dropdown", "children"),
    Output("sixthform-pastoral", "data")
], [
    Input("location", "pathname"),
    Input("location", "search"),
], [State("team-dropdown", "label")])
def update_teams(pathname, search, team):
    # Set teams and cohort from location
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', ['2123'])[0]
    teams = data.get_teams(cohort)
    # Get list of teams
    team = search_dict.get("team", ['All'])[0]
    # Populate the dropdowns
    team_items = [dbc.DropdownMenuItem()]
    for t in ['All'] + teams:
        s = urlencode(query={'cohort': cohort, 'team': t})
        team_items.append(dbc.DropdownMenuItem(t, href=f'{pathname}?{s}'))
    cohort_items = []
    for c in ['2022', '2123']:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    # Get data in scope
    enrolment_docs = data.get_enrolment_by_cohort_team(cohort, team)
    student_ids = [e.get('_id') for e in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    assessment_docs = data.get_data("assessment", "student_id", student_ids)
    kudos_docs = data.get_data("kudos", "student_id", student_ids)
    concern_docs = data.get_data("concern", "student_id", student_ids)
    store_data = {
        "student_ids": student_ids,
        "enrolment_docs": enrolment_docs,
        "attendance_docs": attendance_docs,
        "assessment_docs": assessment_docs,
        "kudos_docs": kudos_docs,
        "concern_docs": concern_docs,
    }
    return (cohort, cohort_items, team, team_items, store_data)
