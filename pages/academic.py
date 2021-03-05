import dash_tabulator
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

academic_header = html.H4(id={
    "type": "text",
    "page": "academic",
    "name": "header"
})
assessment_filter = dcc.Dropdown(id={
    "type": "dropdown",
    "page": "academic",
    "name": "assessment"
}, )

tabs = ["View", "Edit"]
content = [
    dbc.Card(
        [dbc.CardHeader(academic_header),
         dbc.CardBody(assessment_filter)]),
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=t, tab_id=f"academic-tab-{t.lower()}")
                    for t in tabs
                ],
                id=f"academic-tabs",
                card=True,
                active_tab=f"academic-tab-{tabs[0].lower()}",
            )),
        dbc.CardBody(dbc.Row(id="academic-content")),
    ])
]
subject_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "academic",
        "tab": "edit"
    },
    options={"resizableColumns": False, "index": "_id", "layout": "fitDataStretch", "clipboard": True, "selectable": False, "clipboardPasteAction": ns("clipboardPasteAction"), "clipboardCopySelector": "table", "clipboardPasted": ns("clipboardPasted")},
    downloadButtonType={"css": "btn btn-primary", "text": "Download", "type": "csv"},
    theme='bootstrap/tabulator_bootstrap4',
)

assessment_graph = dcc.Graph(
    id={
        "type": "graph",
        "page": "academic",
        "tab": "view",
        "name": "bar"
    },
    figure={
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            }
        }
    },
    config={
        "displayModeBar": False,
    },
    style={'height': '350px'},
)
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
validation_layout = content + [
    subject_table, assessment_graph,
    assessment_colour_dropdown
]
tab_map = {
    "academic-tab-view": [
        dbc.Col([
            assessment_graph,
        ], width=10),
        dbc.Col([html.Div("Colour by GCSE "), assessment_colour_dropdown],
                width=2)
    ],
    "academic-tab-edit": [
        dbc.Col(subject_table, width=12),
    ]
}


@app.callback(
    Output(f"academic-content", "children"),
    [
        Input(f"academic-tabs", "active_tab"),
    ],
)
def get_content(active_tab):
    return tab_map.get(active_tab)


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
    _, _, subject_code = filter_value
    # If the user hasn't selected a subject/assessment yet
    if not assessment_name:
        return [], []
    # If we're here because a cell has been edited
    if changed:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id_x"))
        doc.update({"grade": row.get("grade"),"comment": row.get("comment")})
        data.save_docs([doc])
    # If we're here because data has been pasted
    if row_data:
        assessment_docs = data.get_data("assessment", "assessment_subject", [(assessment_name, subject_code)])
        assessment_df = pd.DataFrame.from_records(assessment_docs)
        try:
            pasted_df = pd.DataFrame.from_records(row_data)[["student_id", "grade", "comment"]]
        except KeyError:
            # Silently fail if student_id, grade, and comment fields were not present
            print("Problematic row data: ", row_data)
        else:
            pasted_df = pasted_df.replace('\r', '', regex=True)
            merged_df = pd.merge(assessment_df,
                                pasted_df,
                                on="student_id")
            merged_df = merged_df.rename(columns={"grade_y": "grade", "comment_y": "comment"}).drop(["grade_x", "comment_x"], axis=1)
            merged_docs = merged_df.to_dict(orient='records')
            data.save_docs(merged_docs)

    assessment_docs = data.get_data("assessment", "assessment_subject", [(assessment_name, subject_code)])
    assessment_df = pd.DataFrame.from_records(assessment_docs)
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
            "editorParams": {"verticalNavigation": "hybrid"},
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
    _, _, subject_code = filter_value
    if not assessment_name:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                }
            }
        }
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "assessment_subject",
                      [(assessment_name, subject_code)]))
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
        column_widths=[0.2, 0.8],
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
    fig.add_trace(bar_trace, row=1, col=1)
    fig.add_trace(scatter_trace, row=1, col=2)
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
    fig.update_layout(margin={'t': 0},
                      autosize=True,
                      plot_bgcolor="#FFF",
                      yaxis_title="Grade")
    return fig


@app.callback([
    Output({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "options"),
    Output({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "value"),
    Output({
        "type": "text",
        "page": "academic",
        "name": "header"
    }, "children"),
], [Input({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_assessment_dropdown(filter_value):
    cohort, _, subject_code = filter_value
    if not (cohort and subject_code):
        return [], "", f"Cohort {cohort}"
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "subject_code", subject_code))
    group_docs = data.get_data("group", "subject_code", subject_code)
    subject = group_docs[0].get("subject_name")
    if assessment_df.empty:
        return [], "", f"Cohort {cohort}, {subject}"
    assessment_list = assessment_df.sort_values(
        by="date", ascending=False)["assessment"].unique().tolist()
    options = [{"label": a, "value": a} for a in assessment_list]
    return options, options[0].get("value"), f"Cohort {cohort}, {subject}"
