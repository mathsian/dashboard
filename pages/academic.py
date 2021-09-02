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

assessment_filter = dcc.Dropdown(id={
    "type": "dropdown",
    "page": "academic",
    "name": "assessment"
}, )

tabs = ["View", "Edit"]
content = [
    dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label=t, tab_id=f"academic-tab-{t.lower()}")
                        for t in tabs
                    ],
                             id=f"academic-tabs",
                             card=True,
                             active_tab=f"academic-tab-{tabs[0].lower()}")
                ],
                        align='end',
                        width=6,
                        lg=4),
                dbc.Col([filters.cohort], width=2, lg=2),
                dbc.Col([filters.subject], width=2, lg=2),
                dbc.Col(assessment_filter),
            ],
                    align='end')
        ]),
        dbc.CardBody(dbc.Row(id="academic-content"),
                     style={
                         "max-height": "70vh",
                         "overflow-y": "auto"
                     }),
    ]),
]

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
validation_layout = content + [
    subject_table, assessment_graph, assessment_colour_dropdown
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
    print(f'Getting results for {filter_value}, {assessment_name}')
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
            # Silently fail if student_id, grade, and comment fields were not present
            print("Problematic row data: ", row_data)
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
                                    [[assessment_name, subject_code, cohort]])
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
], [Input({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_assessment_dropdown(filter_value):
    print(f'Getting assessments for {filter_value}')
    cohort, subject_code = filter_value
    if not (cohort and subject_code):
        return [], ""
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "subject_cohort",
        [subject_code, cohort])
    group_docs = data.get_data("group", "subject_cohort", [subject_code, cohort]
    subject = group_docs[0].get("subject_name")
    if assessment_df.empty:
        return [], ""
    assessment_list = assessment_df.sort_values(
        by="date", ascending=False)["assessment"].unique().tolist()
    options = [{"label": a, "value": a} for a in assessment_list]
    return options, options[0].get("value")


@app.callback(
    [
        Output({
            "type": "filter-dropdown",
            "filter": "subject"
        }, "options"),
        Output({
            "type": "filter-dropdown",
            "filter": "subject"
        }, "value"),
    ],
    [Input({
        "type": "filter-dropdown",
        "filter": "cohort"
    }, "value")],
)
def update_subject_filter(cohort_value):
    print(f'Getting subjects for cohort {cohort_value}')
    subjects = data.get_subjects(cohort_value)
    return [
        [{
            "label": s[0],
            "value": s[0]
        } for s in subjects],
        None,
    ]
