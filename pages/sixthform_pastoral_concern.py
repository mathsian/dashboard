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
        # "layout": "fitDataStretch",
        # "maxHeight": "70vh",
        "clipboard": "copy"
    },
)

layout = dbc.Container(concern_table)


@app.callback(
    Output({
        "type": "table",
        "page": "pastoral",
        "tab": "concern",
    }, "data"),
    [
        Input("sixthform-pastoral", "data"),
    ],
)
def update_pastoral_concern(store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    concern_docs = store_data.get('concern_docs')
    if not concern_docs:
        return []
    concern_df = pd.merge(pd.DataFrame.from_records(enrolment_docs),
                          pd.DataFrame.from_records(concern_docs),
                          how="right",
                          left_on="_id",
                          right_on="student_id").sort_values("date",
                                                             ascending=False)
    return concern_df.to_dict(orient="records")
