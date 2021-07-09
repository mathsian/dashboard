from app import app
import dash_bootstrap_components as dbc
import dash_tabulator
from dash.dependencies import Input, Output, State, ALL
import data
import curriculum
from flask_dance.contrib.google import google
from dash import callback_context
from flask import session
import pandas as pd
from dash_extensions.javascript import Namespace
ns = Namespace("myNameSpace", "tabulator")

tabs = ["Kudos", "Concern"]
content = [
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [dbc.Tab(label=t, tab_id=f"my-tab-{t.lower()}") for t in tabs],
                id="my-tabs",
                card=True,
                active_tab=f"my-tab-{tabs[0].lower()}")),
        dbc.CardBody(dbc.Row(id="my-content"),
style={
        "max-height": "70vh",
        "overflow-y": "auto"
    },
        )
    ])
]

kudos_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "my",
        "tab": "kudos"
    },
    columns=[
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
            "title": "Date",
            "field": "date",
            "width": "10%"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "20%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Value",
            "field": "ada_value",
            "editor": "select",
            "editorParams": {
                "values": curriculum.values
            },
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.values
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Points",
            "field": "points",
            "editor": "select",
            "editorParams": {
                "values": [1, 3, 5]
            },
            "width": "10%",
            "topCalc": "sum",
        },
        {
            "title": "Description",
            "field": "description",
            "editor": "textarea",
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "formatter": "buttonCross",
            "cellClick": ns("deleteRow"),
            "width": "5%",
            "headerSort": False,
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "maxHeight": "95%",
        "index": "_id",
    },
)
concern_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "my",
        "tab": "concern"
    },
    columns=[
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
            "title": "Date",
            "field": "date",
            "width": "10%"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "15%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Category",
            "field": "category",
            "editor": "select",
            "editorParams": {
                "values": curriculum.concern_categories
            },
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_categories
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Description",
            "field": "description",
            "editor": "textarea",
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Additional",
            "field": "discrimination",
            "editor": "select",
            "editorParams": {
                "values": curriculum.concern_discrimination
            },
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_discrimination
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "formatter": "buttonCross",
            "cellClick": ns("deleteRow"),
            "width": "5%",
            "headerSort": False,
        },
    ],
    theme='bootstrap/tabulator_bootstrap4',
    options={
        "maxHeight": "95%",
        "index": "_id",
    },
)
validation_layout = content + [kudos_table, concern_table]
tab_map = {
    "my-tab-kudos": [dbc.Col(kudos_table)],
    "my-tab-concern": [dbc.Col(concern_table)],
}


@app.callback(Output("my-content", "children"),
              [Input("my-tabs", "active_tab")])
def get_content(active_tab):
    return tab_map.get(active_tab)


@app.callback(Output({
    "type": "table",
    "page": "my",
    "tab": "kudos"
}, "data"), [
    Input({
        "type": "table",
        "page": "my",
        "tab": "kudos"
    }, "cellEdited"),
    Input({
        "type": "table",
        "page": "my",
        "tab": "kudos"
    }, "dataChanged")
])
def update_kudos_table(changed, dataChanged):
    trigger = callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id"))
        doc.update({
            "description": row.get("description"),
            "points": row.get("points"),
            "ada_value": row.get("ada_value")
        })
        data.save_docs([doc])
    elif "dataChanged" in trigger:
        # For now we are here because a row has been deleted
        kudos_docs = data.get_data("kudos", "from", [session.get('email')])
        keep_ids = [d.get("_id") for d in dataChanged]
        deleted_ids = [
            d.get("_id") for d in kudos_docs if d.get("_id") not in keep_ids
        ]
        data.delete_docs(deleted_ids)
    kudos_docs = data.get_data("kudos", "from", [session.get('email')])
    kudos_df = pd.DataFrame(kudos_docs)
    student_ids = list(kudos_df["student_id"].unique())
    enrolment_docs = data.get_data("enrolment", "_id", student_ids)
    enrolment_df = pd.DataFrame(enrolment_docs)
    merged_df = kudos_df.merge(enrolment_df,
                               left_on="student_id",
                               right_on="_id",
                               how="inner")
    merged_df = merged_df.rename(columns={
        "_id_x": "_id",
        "type_x": "type",
        "_rev_x": "_rev"
    })[[
        "_id", "_rev", "date", "given_name", "family_name", "ada_value",
        "points", "description"
    ]]
    return merged_df.to_dict(orient='records')


@app.callback(Output({
    "type": "table",
    "page": "my",
    "tab": "concern"
}, "data"), [
    Input({
        "type": "table",
        "page": "my",
        "tab": "concern"
    }, "cellEdited"),
    Input({
        "type": "table",
        "page": "my",
        "tab": "concern"
    }, "dataChanged"),
    Input({
        "type": "table",
        "page": "my",
        "tab": "concern"
    }, "rowDeleted")
])
def update_concern_table(changed, dataChanged, deleted):
    trigger = callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id"))
        doc.update({
            "description": row.get("description"),
            "category": row.get("category"),
            "discrimination": row.get("discrimination")
        })
        data.save_docs([doc])
    elif "dataChanged" in trigger:
        # For now we are here because a row has been deleted
        concern_docs = data.get_data("concern", "from", [session.get('email')])
        keep_ids = [d.get("_id") for d in dataChanged]
        deleted_ids = [
            d.get("_id") for d in concern_docs if d.get("_id") not in keep_ids
        ]
        data.delete_docs(deleted_ids)
    elif "rowDeleted" in trigger:
        # This callback is not implemented in dash-tabulator yet
        # This is here for when it is or when we do it ourselves
        row = deleted.get("row")
        doc = data.get_doc(row.get("_id"))
        data.delete_docs([doc])
    concern_docs = data.get_data("concern", "from", [session.get('email')])
    concern_df = pd.DataFrame(concern_docs)
    student_ids = list(concern_df["student_id"].unique())
    enrolment_docs = data.get_data("enrolment", "_id", student_ids)
    enrolment_df = pd.DataFrame(enrolment_docs)
    merged_df = concern_df.merge(enrolment_df,
                                    left_on="student_id",
                                    right_on="_id",
                                    how="inner")
    merged_df = merged_df.rename(columns={
        "_id_x": "_id",
        "type_x": "type",
        "_rev_x": "_rev"
    })[[
        "_id", "_rev", "date", "given_name", "family_name", "category",
        "discrimination", "description"
    ]]
    return merged_df.to_dict(orient='records')
