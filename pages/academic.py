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
subject_table = dash_table.DataTable(id={
    "type": "table",
    "page": "academic",
    "tab": "edit"
},
                                     columns=[
                                         {
                                             "name": "Given name",
                                             "id": "given_name",
                                             "editable": False
                                         },
                                         {
                                             "name": "Family name",
                                             "id": "family_name",
                                             "editable": False
                                         },
                                         {
                                             "name": "Grade",
                                             "id": "grade",
                                             "type": "text",
                                             "presentation": "dropdown",
                                             "editable": True
                                         },
                                         {
                                             "name": "Comment",
                                             "id": "comment",
                                             "type": "text",
                                             "presentation": "input",
                                             "editable": True
                                         },
                                     ],
                                     editable=True,
                                     style_cell={
                                         "textAlign": "left",
                                         "height": "auto",
                                         "whiteSpace": "normal",
                                     },
                                     sort_action='native',
                                     filter_action='native',
                                     sort_by=[{
                                         "column_id": "given_name",
                                         "direction": "asc"
                                     }, {
                                         "column_id": "family_name",
                                         "direction": "asc"
                                     }])

assessment_download_link = html.A("Download csv",
                                  id={
                                      "type": "link",
                                      "page": "academic",
                                      "tab": "edit",
                                      "name": "download"
                                  },
                                  hidden=True,
                                  href="",
                                  target="_blank")

assessment_toast = dbc.Toast("Testing",
                             id={
                                 "type": "toast",
                                 "page": "academic",
                                 "tab": "edit"
                             },
                             is_open=False,
                             duration=3000)
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
                                                  "label": "Computer Science",
                                                  "value": "gc-comp.sci"
                                              },
                                          ],
                                          value="gc-ma")
validation_layout = content + [
    assessment_toast, subject_table, assessment_graph,
    assessment_colour_dropdown
]
tab_map = {
    "academic-tab-view": [
        dbc.Col([
            assessment_graph,
        ], width=8),
        dbc.Col([html.Div("Colour by GCSE "), assessment_colour_dropdown],
                width=3)
    ],
    "academic-tab-edit": [
        dbc.Col(subject_table),
        dbc.Col([assessment_download_link, assessment_toast], width=3)
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
    Output(
        {
            "type": "link",
            "page": "academic",
            "tab": "edit",
            "name": "download"
        }, "hidden"),
    Output(
        {
            "type": "link",
            "page": "academic",
            "tab": "edit",
            "name": "download"
        }, "download"),
    Output(
        {
            "type": "link",
            "page": "academic",
            "tab": "edit",
            "name": "download"
        }, "href"),
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "dropdown"),
], [
    Input({
        "type": "dropdown",
        "page": "academic",
        "name": "assessment"
    }, "value")
], [State({
    "type": "filter-dropdown",
    "filter": ALL
}, "value")])
def update_subject_table(assessment_name, filter_value):
    _, _, subject_code = filter_value
    if not assessment_name:
        return [], True, "", "", {}
    assessment_df = pd.DataFrame.from_records(
        data.get_data("assessment", "assessment_subject",
                      [(assessment_name, subject_code)]))
    student_ids = assessment_df["student_id"].tolist()
    enrolment_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "_id", student_ids))
    merged_df = pd.merge(assessment_df,
                         enrolment_df,
                         left_on='student_id',
                         right_on='_id',
                         how='inner')
    subtype = merged_df.iloc[0]["subtype"]
    dropdown = {
        "grade": {
            "options": [{
                "label": s,
                "value": s
            } for s in curriculum.scales.get(subtype)]
        }
    }
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(
        merged_df.to_csv(index=False, encoding="utf-8"))
    return merged_df.to_dict(
        orient='records'
    ), False, f"{subject_code} {assessment_name}.csv", csv_string, dropdown


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
    fig = go.Figure(
        go.Scatter(
            x=merged_df["aps"],
            y=merged_df["grade"],
            marker=dict(
                color=merged_df[colour_code],
                colorscale='viridis',
                showscale=True,
                size=20,
            ),
            customdata=np.stack(
                (merged_df["given_name"], merged_df["family_name"]), axis=-1),
            hovertemplate=
            "%{customdata[0]} %{customdata[1]}: %{y}<br>APS: %{x:.1f}<extra></extra>",
            mode='markers'))
    fig.update_yaxes(
        categoryorder='array',
        categoryarray=curriculum.scales.get(subtype),
    )
    fig.update_layout(margin={'t': 0},
                      autosize=True,
                      xaxis_title="GCSE Average Point Score",
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


@app.callback([
    Output({
        "type": "toast",
        "page": "academic",
        "tab": "edit",
    }, "is_open"),
    Output({
        "type": "toast",
        "page": "academic",
        "tab": "edit",
    }, "children"),
], [
    Input({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data_timestamp"),
], [
    State({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data"),
    State({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data_previous"),
],
              prevent_initial_call=True)
def update_subject_toast(data_ts, table_data, previous_data):
    if not previous_data:
        return False, "No previous data"
    df, df_previous = pd.DataFrame(table_data).sort_index(), pd.DataFrame(
        previous_data).sort_index()
    changes = df_previous.compare(df)
    changed = changes.index
    if len(changed) != 1:
        return True, "Multiple changes, weirdly"
    assessment_doc = df.rename(columns={
        "_id_x": "_id",
        "_rev_x": "_rev",
        "cohort_x": "cohort",
        "type_x": "type"
    }).loc[changed, [
        "_id", "_rev", "type", "subtype", "date", "student_id", "grade",
        "comment", "cohort", "group_id", "subject_code", "subject_name",
        "assessment"
    ]].to_dict(orient='records')
    data.save_docs(assessment_doc)
    return True, [
        html.Div(f"{d.get('grade')}, {d.get('comment')}")
        for d in assessment_doc
    ]
