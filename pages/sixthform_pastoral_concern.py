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

# Concern tab content
concern_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
    },
    columns=[
        {
            "title": "Given name",
            "field": "given_name"
        },
        {
            "title": "Family name",
            "field": "family_name"
        },
        {
            "title": "Date",
            "field": "date"
        },
        {
            "title": "Category",
            "field": "category"
        },
        {
            "title": "Raised by",
            "field": "from"
        },
        {
            "title": "Description",
            "field": "description"
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "resizableColumns": False,
        "layout": "fitDataStretch",
        "maxHeight": "70vh",
        "clipboard": "copy"
    },
)

layout = dbc.Col(width=12, children=concern_table)

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

