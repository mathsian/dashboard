from app import app
import dash_tabulator
from dash.dependencies import Input, Output
import data
import curriculum
from dash import callback_context
import dash_bootstrap_components as dbc
from flask import request
import pandas as pd
from dash_extensions.javascript import Namespace
ns = Namespace("myNameSpace", "tabulator")

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
            "title": "Stage",
            "field": "stage",
            "editor": "select",
            "editorParams": {
                "values": curriculum.concern_stages
            },
            "width": "10%",
            "headerFilter": "select",
            "headerFilterParams": {
                "values": curriculum.concern_stages
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
        "height": "70vh",
        "pagination": "local",
        "index": "_id",
    },
)

layout = dbc.Container(concern_table)


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
            "stage": row.get("stage"),
            "discrimination": row.get("discrimination")
        })
        data.save_docs([doc])
    elif "dataChanged" in trigger:
        # For now we are here because a row has been deleted
        concern_docs = data.get_data("concern", "from", [request.headers.get('X-Email')])
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
    concern_docs = data.get_data("concern", "from", [request.headers.get('X-Email')])
    # If email has no concerns then concern docs will be empty
    # which means concern_df will have no columns and throw an error when we use one
    # better just save everyone's time and bail now
    if not concern_docs:
        return []
    concern_df = pd.DataFrame(concern_docs).sort_values('date', ascending=False)
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
        "stage", "discrimination", "description"
    ]]
    return merged_df.to_dict(orient='records')
