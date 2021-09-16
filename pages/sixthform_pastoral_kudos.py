import filters
import dash_tabulator
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

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
    } for v in curriculum.values] + [{
        "title": "Total",
        "field": "total",
        "hozAlign": "right",
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

layout = dbc.Row([
    dbc.Col(width=4, children=[kudos_radar]),
    dbc.Col(width=8, children=[kudos_table]),
])


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
    ], [Input("sixthform-pastoral", "data"),
    ],
    [State({
        "type": "graph",
        "page": "pastoral",
        "tab": "kudos",
    }, "figure")])
def update_pastoral_kudos(store_data, current_figure):
    enrolment_docs = store_data.get('enrolment_docs')
    kudos_docs = store_data.get('kudos_docs')
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
