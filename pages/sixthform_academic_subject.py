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

ns = Namespace("myNameSpace", "tabulator")

subject_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "academic",
        "tab": "edit"
    },
    options={
        "maxHeight": "60vh",
        "placeholder": "Select a subject",
        "resizableColumns": False,
        "index": "_id",
        "layout": "fitDataStretch",
        "clipboard": True,
        "selectable": False,
        "clipboardPasteAction": ns("clipboardPasteAction"),
        "clipboardCopySelector": "table",
        "clipboardPasted": ns("clipboardPasted")
    },
    downloadButtonType={
        "css": "btn btn-primary",
        "text": "Download",
        "type": "csv"
    },
    theme='bootstrap/tabulator_bootstrap4',
)

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
        dbc.Col([filters.subject], width=3),
        dbc.Col([filters.assessment], width=3),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([assessment_graph])
            ]),
            dbc.Row([
                dbc.Col([assessment_colour_dropdown], width=1)
            ])]
            , width=6),
        dbc.Col([subject_table], width=6),
    ])
]


@app.callback([
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data"),
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "columns"),
], [
    Input({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "value"),
    Input({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "cellEdited"),
    Input({
        "type": "table",
        "page": "academic",
        "tab": "edit",
    }, "clipboardPasted")
], [State({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_subject_table(assessment_name, changed, row_data, filter_value):
    cohort, subject_code = filter_value
    # If the user hasn't selected a subject/assessment yet
    if not assessment_name:
        return [], []
    trigger = dash.callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id_x"))
        doc.update({"grade": row.get("grade"), "comment": row.get("comment")})
        data.save_docs([doc])
    elif "clipboardPasted" in trigger:
        # If we're here because data has been pasted
        assessment_docs = data.get_data("assessment",
                "assessment_subject_cohort",
                                        [(assessment_name, subject_code, cohort)])
        assessment_df = pd.DataFrame.from_records(assessment_docs)
        try:
            pasted_df = pd.DataFrame.from_records(row_data)[[
                "student_id", "grade", "comment"
            ]]
        except KeyError:
            pass
            # Silently fail if student_id, grade, and comment fields were not present
        else:
            pasted_df = pasted_df.replace('\r', '', regex=True)
            merged_df = pd.merge(assessment_df, pasted_df, on="student_id")
            merged_df = merged_df.rename(columns={
                "grade_y": "grade",
                "comment_y": "comment"
            }).drop(["grade_x", "comment_x"], axis=1)
            merged_docs = merged_df.to_dict(orient='records')
            data.save_docs(merged_docs)

    assessment_docs = data.get_data("assessment", "assessment_subject_cohort",
                                    [(assessment_name, subject_code, cohort)])
    assessment_df = pd.DataFrame.from_records(assessment_docs).sort_values(
        by='student_id')
    student_ids = assessment_df["student_id"].tolist()
    enrolment_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "_id", student_ids))
    merged_df = pd.merge(assessment_df,
                         enrolment_df,
                         left_on='student_id',
                         right_on='_id',
                         how='inner')
    subtype = merged_df.iloc[0]["subtype"]
    columns = [
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Email",
            "field": "student_email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "20%"
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "20%"
        },
        {
            "title": "Grade",
            "field": "grade",
            "editor": "select",
            "editorParams": {
                "values": curriculum.scales.get(subtype)
            },
            "width": "15%"
        },
        {
            "title": "Comment",
            "field": "comment",
            "editor": "textarea",
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
        },
    ]
    return merged_df.to_dict(orient='records'), columns


@app.callback(
    Output(
        {
            "type": "graph",
            "page": "academic",
            "tab": "view",
            "name": "bar",
        }, "figure"),
    [
        Input({
            "type": "dropdown",
            "page": "academic",
            "name": "assessment"
        }, "value"),
        Input(
            {
                "type": "dropdown",
                "page": "academic",
                "tab": "view",
                "name": "colour"
            }, "value"),
    ], [State({
        "type": "filter-dropdown",
        "filter": ALL
    }, "value")])
def update_subject_graph(assessment_name, colour_code, filter_value):
    cohort, subject_code = filter_value
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



