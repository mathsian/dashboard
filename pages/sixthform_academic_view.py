import filters
import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import urllib
from app import app
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

assessment_graph = dcc.Graph(id={
    "type": "graph",
    "page": "academic",
    "tab": "view",
    "name": "bar"
},
                             config={
                                 "displayModeBar": False,
                             },
                             figure={
                                 "layout": {
                                     "xaxis": {
                                         "visible": False
                                     },
                                     "yaxis": {
                                         "visible": False
                                     },
                                     "height": 320
                                 }
                             })
assessment_colour_dropdown = dcc.Dropdown(id={
    "page": "academic",
    "tab": "view",
    "type": "dropdown",
    "name": "colour"
},
                                          options=[
                                              {
                                                  "label": "Maths",
                                                  "value": "gc-ma"
                                              },
                                              {
                                                  "label": "English",
                                                  "value": "gc-en"
                                              },
                                              {
                                                  "label": "Comp Sci",
                                                  "value": "gc-comp.sci"
                                              },
                                          ],
                                          value="gc-ma")

layout = [
    dbc.Row([
        dbc.Col([
            dbc.Row([dbc.Col([assessment_graph])]),
            dbc.Row([dbc.Col([assessment_colour_dropdown], width=3)])
        ])
    ])
]


@app.callback(
    Output(
        {
            "type": "graph",
            "page": "academic",
            "tab": "view",
            "name": "bar",
        }, "figure"),
    [
        Input("assessment-dropdown", "label"),
        Input(
            {
                "type": "dropdown",
                "page": "academic",
                "tab": "view",
                "name": "colour"
            }, "value"),
    ], [
        State("academic-cohort-dropdown", "label"),
        State("subject-dropdown", "label"),
        ])
def update_subject_graph(assessment_name, colour_code, cohort, subject_code):
    if not assessment_name:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "height": 320
            }
        }
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "assessment_subject_cohort",
                      [(assessment_name, subject_code, cohort)]))
    subtype = assessment_df.iloc[0]["subtype"]
    enrolment_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "_id",
                      assessment_df["student_id"].to_list()))
    merged_df = assessment_df.merge(enrolment_df,
                                    left_on="student_id",
                                    right_on="_id",
                                    how="inner")
    fig = sp.make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        shared_xaxes=False,
        column_widths=[3, 7],
    )
    scatter_trace = go.Scatter(
        x=merged_df["aps"],
        y=merged_df["grade"],
        marker=dict(
            color=merged_df[colour_code],
            colorbar=dict(tickmode='array',
                          tickvals=list(range(-1, 10)),
                          ticktext=["missing"] + list(range(10))),
            cmin=-1,
            cmax=9,
            colorscale=px.colors.sequential.thermal,
            showscale=True,
            size=16,
            opacity=0.8,
        ),
        showlegend=False,
        customdata=np.stack((merged_df["given_name"], merged_df["family_name"],
                             merged_df[colour_code]),
                            axis=-1),
        hovertemplate=
        "%{customdata[0]} %{customdata[1]}: %{y}<br>APS: %{x:.1f}<br>" +
        colour_code + ": %{customdata[2]}<extra></extra>",
        mode='markers')
    bar_trace = go.Histogram(
        y=merged_df["grade"],
        histfunc='count',
        histnorm='percent',
        orientation='h',
        showlegend=False,
        hovertemplate="%{y} %{x:.1f}<extra></extra>",
    )
    fig.update_yaxes(
        categoryorder='array',
        categoryarray=curriculum.scales.get(subtype),
    )
    fig.update_xaxes(
        title_text="GCSE Average Point Score",
        row=1,
        col=2,
    )
    fig.update_xaxes(
        title_text="Percent",
        row=1,
        col=1,
    )
    fig.update_layout(plot_bgcolor='#FFF',
                      height=320,
                      margin={
                          "pad": 10,
                          "t": 0,
                          "autoexpand": False
                      })
    fig.add_trace(bar_trace, row=1, col=1)
    fig.add_trace(scatter_trace, row=1, col=2)
    return fig
