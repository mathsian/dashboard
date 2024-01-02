from app import app
from dash import html
import dash_bootstrap_components as dbc
import dash_tabulator
from dash.dependencies import Input, Output, State, ALL
import data
import curriculum
from dash import callback_context
from flask import request
import pandas as pd
from dash_extensions.javascript import Namespace
from icecream import ic

ns = Namespace("myNameSpace", "tabulator")

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
    #    "maxHeight": "95%",
        "index": "_id",
        "pagination": "local",
        "height": "70vh"
    },
)

layout = dbc.Container(kudos_table)


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
            "points": int(row.get("points")), # not sure why this wouldn't be an int be to be safe
            "ada_value": row.get("ada_value")
        })
        data.save_docs([doc])
    elif "dataChanged" in trigger:
        # For now we are here because a row has been deleted
        kudos_docs = data.get_data("kudos", "from", [request.headers.get('X-Email')])
        keep_ids = [d.get("_id") for d in dataChanged]
        deleted_ids = [
            d.get("_id") for d in kudos_docs if d.get("_id") not in keep_ids
        ]
        data.delete_docs(deleted_ids)
    kudos_docs = data.get_data("kudos", "from", [request.headers.get('X-Email')])
    if not kudos_docs:
        return []
    kudos_df = pd.DataFrame(kudos_docs).sort_values('date', ascending=False)
    student_ids = list(kudos_df["student_id"].unique())
    enrolment_docs = data.get_data("enrolment", "_id", student_ids)
    if not enrolment_docs:
        return []
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
