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

notes_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "my",
        "tab": "notes"
    },
    columns=[
        {
            "title": "Given name",
            "field": "given_name",
            "width": "10%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
            "frozen": "true",
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "20%",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
            "frozen": "true",
        },
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
            "title": "Category",
            "field": "category",
            "width": "15%",
            "editor": "select",
            "editorParams": {
                "values": ['Absence', 'Lateness']
            },
            "headerFilter": 'select',
            "headerFilterParams": {
                "values": ['Absence', 'Lateness']
            },
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Comment",
            "field": "comment",
            "editor": "textarea",
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
            "headerFilter": True,
            "headerFilterPlaceholder": "filter",
        },
        {
            "title": "Include in report",
            "field": "report",
            "align": "center",
            "editor": True,
            "formatter": "tickCross",
            "formatterParams": {"crossElement": False},
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

layout = dbc.Container(notes_table)


@app.callback(Output({
    "type": "table",
    "page": "my",
    "tab": "notes"
}, "data"), [
    Input({
        "type": "table",
        "page": "my",
        "tab": "notes"
    }, "cellEdited"),
    Input({
        "type": "table",
        "page": "my",
        "tab": "notes"
    }, "dataChanged")
])
def update_notes_table(changed, dataChanged):
    trigger = callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id"))
        doc.update({
            "comment": row.get("comment"),
            "report": row.get("report"),
            "category": row.get("category"),
        })
        data.save_docs([doc])
    elif "dataChanged" in trigger:
        # For now we are here because a row has been deleted
        notes_docs = data.get_data("note", "from", [request.headers.get('X-Email')])
        keep_ids = [d.get("_id") for d in dataChanged]
        deleted_ids = [
            d.get("_id") for d in notes_docs if d.get("_id") not in keep_ids
        ]
        data.delete_docs(deleted_ids)
    notes_docs = data.get_data("note", "from", [request.headers.get('X-Email')])
    if not notes_docs:
        return []
    notes_df = pd.DataFrame(notes_docs).sort_values('date', ascending=False)
    student_ids = list(notes_df["student_id"].unique())
    enrolment_docs = data.get_data("enrolment", "_id", student_ids)
    if not enrolment_docs:
        return []
    enrolment_df = pd.DataFrame(enrolment_docs)
    merged_df = notes_df.merge(enrolment_df,
                               left_on="student_id",
                               right_on="_id",
                               how="inner")
    merged_df = merged_df.rename(columns={
        "_id_x": "_id",
        "type_x": "type",
        "_rev_x": "_rev"
    })[[
        "_id", "_rev", "date", "given_name", "family_name", "comment",
        "report", "category"
    ]]
    return merged_df.to_dict(orient='records')
