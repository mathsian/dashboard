import dash_tabulator
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

result_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "section": "apprenticeships",
        "page": "academic",
        "tab": "edit"
    },
    options={
        "layout": "fitDataTable",
        "placeholder": "Select a module",
        "resizableColumns": False,
        "index": "_id",
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
#layout = dbc.Row(dbc.Col([result_table]))
layout = dbc.Container([
    html.H4(id={"type": "text", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}),
    result_table])


@app.callback([
    Output(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "edit"
        }, "data"),
    Output(
        {
            "type": "table",
            "page": "academic",
            "section": "apprenticeships",
            "tab": "edit"
        }, "columns"),
    Output(
        {"type": "text", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}, "children")
], [
    Input("apprenticeships-academic-store", "data"),
    Input(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "edit"
        }, "cellEdited"),
    Input(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "edit",
        }, "clipboardPasted")
])
def update_subject_table(store_data, changed, row_data):
    instance_dict = store_data.get("instance", {})
    if not instance_dict:
        return [], [], "No instance selected"
    trigger = dash.callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        pass
        # row = changed.get("row")
        # doc = data.get_doc(row.get("_id_x"))
        # doc.update({"grade": row.get("grade"), "comment": row.get("comment")})
        # data.save_docs([doc])
    elif "clipboardPasted" in trigger:
        pass
        # # If we're here because data has been pasted
        # assessment_docs = store_data.get("assessment_docs")
        # assessment_df = pd.DataFrame.from_records(assessment_docs)
        # try:
        #     pasted_df = pd.DataFrame.from_records(row_data)[[
        #         "student_id", "grade", "comment"
        #     ]]
        # except KeyError:
        #     pass
        #     # Silently fail if student_id, grade, and comment fields were not present
        # else:
        #     pasted_df = pasted_df.replace('\r', '', regex=True)
        #     merged_df = pd.merge(assessment_df, pasted_df, on="student_id")
        #     merged_df = merged_df.rename(columns={
        #         "grade_y": "grade",
        #         "comment_y": "comment"
        #     }).drop(["grade_x", "comment_x"], axis=1)
        #     merged_docs = merged_df.to_dict(orient='records')
        #     data.save_docs(merged_docs)

    columns_start = [
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Email",
            "field": "email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
       {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
            "widthGrow": 2
        },
        {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
            "widthGrow": 2
        }]

    components_df = pd.DataFrame.from_records(app_data.get_results_for_instance_code(instance_dict.get("instance_code")))
    components_df.eval("weighted_value = value * weight", inplace=True)
    results_df = components_df.groupby("student_id").sum().eval("total = weighted_value / weight")["total"].round(0).astype("Int64")
    # Number duplicates
    components_df["component_name"] = components_df["component_name"] + components_df.groupby(["student_id", "component_name"]).cumcount().astype(str).replace('0', '')
    components_df = components_df.set_index(["student_id", "given_name", "family_name", "component_name"])[["value", "capped"]]
    components_df = components_df.unstack().swaplevel(axis=1).sort_index(axis=1, ascending=[True, False])
    component_columns = components_df.columns.to_flat_index()
    components_df.columns = [":".join(c) for c in components_df.columns.to_flat_index()]
    components_df = components_df.join(results_df).reset_index()
    columns_middle = []
    for component, column_type in component_columns:
        if column_type == 'value':
            columns_middle.append({"title": component, "field": f'{component}:value', "widthGrow": 1})
        else:
            columns_middle.append({"title": "Cap", "field": f'{component}:capped', "formatter": "tickCross", "formatterParams": {"crossElement": False}, "widthGrow": 1})
    columns_end = [{
            "title": "Total",
            "field": "total",
            "widthGrow": 1
        },
                       ]

    heading = f'{instance_dict.get("module_name")} - {instance_dict.get("instance_code")} - {instance_dict.get("start_date")}'
    return components_df.to_dict(orient='records'), columns_start + columns_middle + columns_end, heading
