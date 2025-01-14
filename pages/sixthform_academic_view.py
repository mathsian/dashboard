import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
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
                                          value="gc-ma",
                                          clearable=False)

layout = dbc.Container([
            dbc.Row([dbc.Col([assessment_colour_dropdown], width=3)], justify='end'),
            dbc.Row([dbc.Col([assessment_graph])]),
        ])


@app.callback(
    Output(
        {
            "type": "graph",
            "page": "academic",
            "tab": "view",
            "name": "bar",
        }, "figure"),
    [
        Input("sixthform-academic-store", "data"),
        Input(
            {
                "type": "dropdown",
                "page": "academic",
                "tab": "view",
                "name": "colour"
            }, "value"),
    ], [
        State("subject-dropdown", "label"),
        ])
def update_subject_graph(store_data, colour_code, subject_code):
    assessment_subject_cohort = store_data.get("assessment_subject_cohort")
    assessment_docs = data.get_data("assessment", "assessment_subject_cohort",
                                    [assessment_subject_cohort])
    assessment_df = pd.DataFrame.from_records(assessment_docs)
    if not store_data:
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
    subtype = assessment_df.iloc[0]["subtype"]
    enrolment_df = pd.DataFrame.from_records(store_data.get("enrolment_docs"))
    # Need a number for GCSE: use -1 for missing ''
    enrolment_df['gc-comp.sci'].where(enrolment_df['gc-comp.sci'] != '', -1, inplace=True)
    enrolment_df['gc-ma'].where(enrolment_df['gc-ma'] != '', -1, inplace=True)
    enrolment_df['gc-en'].where(enrolment_df['gc-en'] != '', -1, inplace=True)
    enrolment_df['aps'].where(enrolment_df['aps'] != '', -1, inplace=True)

    merged_df = assessment_df.merge(enrolment_df,
                                    left_on="student_id",
                                    right_on="_id",
                                    how="inner")
    if subtype == 'Percentage':
        # We need numeric grades otherwise the histogram will think this is categorical
        merged_df["grade"] = pd.to_numeric(merged_df["grade"], errors='coerce')

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
                          ticktext=["n/a"] + list(range(10))),
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
    if subtype == 'Percentage':
        bar_trace = go.Histogram(
            y=merged_df["grade"],
            histfunc='count',
            histnorm='percent',
            orientation='h',
            showlegend=False,
            ybins={"start": 0, "end": 100, "size": 10},
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
        )
    else:
        bar_trace = go.Histogram(
            y=merged_df["grade"],
            histfunc='count',
            histnorm='percent',
            orientation='h',
            showlegend=False,
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
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
                          "autoexpand": True
                      })
    fig.add_trace(bar_trace, row=1, col=1)
    fig.add_trace(scatter_trace, row=1, col=2)
    return fig
