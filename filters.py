from urllib.parse import parse_qs, urlparse
import dash.callback_context as ctx
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

from app import app
import data

cohort = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "cohort"
    },
    placeholder="Select a cohort",
    options=[{
        "label": s,
        "value": s
    } for s in ["1921", "2022", "2123"]],
    value="2123",
    clearable=False,
    persistence=True,
    persistence_type="local",
    searchable=False,
)
team = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "team"
    },
    placeholder="All",
    persistence=True,
    persistence_type="local",
    searchable=False,
)

subject = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "subject"
    },
    placeholder="Select a subject",
    persistence=True,
    persistence_type="local",
    searchable=False,
)

assessment = dcc.Dropdown(id={
    "type": "dropdown",
    "page": "academic",
    "name": "assessment"
},
                                 persistence=True,
                                 persistence_type='local')


@app.callback(
    Output({
        "type": "filter-dropdown",
        "filter": "cohort"
    }, "value"),
    [
        Input({"location": "search"})
    ],
    [
        State({
        "type": "filter-dropdown",
        "filter": "cohort"
        }, "value")
    ]
    )
def update_cohort_value(search, cohort_value):
    filter_dict = parse_qs(search.removeprefix('?'))
    cohort_value = filter_dict.get("cohort", cohort_value)
    return cohort_value


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
    [
        Input({"location": "search"}),
        Input({
        "type": "filter-dropdown",
        "filter": "cohort"
    }, "value")],
    [
        State({"history": "data"}),
        State({"location": "pathname"}),
        State({
            "type": "filter-dropdown",
            "filter": "team"
        }, "options"),
        State({
            "type": "filter-dropdown",
            "filter": "team"
        }, "value"),

    ]
)
def update_team_filter(search, cohort_value, history, pathname, team_options, team_value):
    teams = data.get_teams(cohort_value)
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if "search" in input_id:
        search_dict = parse_qs(search.removeprefix('?'))
        if team := search_dict.get("team", False) and team in teams:
            history.append(pathname+'?'+search)
            team_value = team
        elif team_value not in teams:
            team_value = teams[0]
    else:

    return ([{"label": t, "value": t} for t in teams], team_value)

#
#@app.callback(
#        Output({
#            "type": "filter-dropdown",
#            "filter": "subject"
#        }, "options"),
#    [Input({
#        "type": "filter-dropdown",
#        "filter": "cohort"
#    }, "value")],
#)
#def update_subject_filter(cohort_value):
#    subjects = data.get_subjects(cohort_value)
#    return [{
#            "label": subject_name,
#            "value": subject_code
#        } for subject_code, subject_name in subjects]
#
#
#@app.callback(
#    Output({
#        "type": "dropdown",
#        "page": "academic",
#        "name": "assessment"
#    }, "options"),
#    [Input({
#    "type": "filter-dropdown",
#    "filter": ALL
#}, "value")])
#def update_assessment_dropdown(filter_value):
#    cohort, subject_code = filter_value
#    if not (cohort and subject_code):
#        return []
#    assessment_docs = data.get_data("assessment", "subject_cohort",
#                      (subject_code, cohort))
#    assessment_df = pd.DataFrame.from_records(assessment_docs)
#    if assessment_df.empty:
#        return []
#    assessment_list = assessment_df.sort_values(
#        by="date", ascending=False)["assessment"].unique().tolist()
#    options = [{"label": a, "value": a} for a in assessment_list]
#    return options
#
