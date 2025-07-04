from flask import request
import dash_tabulator
import dash
from dash.dash import no_update
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import numpy as np
from icecream import ic

from app import app
import app_data
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
        #"height": "65vh",
        "placeholder": "Select a module",
        "resizableColumns": False,
        "index": "_id",
        "clipboard": True,
        "selectable": False,
        "clipboardPasteAction": ns("clipboardPasteAction"),
        "clipboardCopySelector": "table",
        "clipboardPasted": ns("clipboardPasted"),
        "clipboardCopyConfig": {"formatCells": False},
    },
    theme='bootstrap/tabulator_bootstrap4',
)
clipboard = dcc.Clipboard(id={"type": "clipboard", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}, style={'display': 'inline-block', 'margin-left': '10px'})
#layout = dbc.Row(dbc.Col([result_table]))
layout = dbc.Container([
    html.H4(id={"type": "text", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}),
    html.Span(["Copy to clipboard", clipboard]),
    result_table])

@app.callback(
Output(
    {"type": "clipboard", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}, 'content'
),
Input(
    {"type": "clipboard", "page": "academic", "section": "apprenticeship", "tab": "edit", "name": "header"}, 'n_clicks'
),
State(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "academic",
            "tab": "edit"
        }, "data")
)
def update_clipboard(n_clicks, data):
    if not data:
        raise dash.exceptions.PreventUpdate
    columns = [{
        "title": "Given name",
        "field": "given_name",
    }, {
        "title": "Family name",
        "field": "family_name",
    }, {
        "title": "Student ID",
        "field": "student_id",
    }, {
        "title": "Email",
        "field": "college_email",
    }]

    df = pd.DataFrame(data)
    components = [{'title': c.split(':')[0], 'field':c} for c in df.columns if ':value' in c]
    columns = columns + components

    fields = [c.get('field') for c in columns]
    titles = [c.get('title') for c in columns]
    renamer = {f: t for (f, t) in zip(fields, titles)}
    renamed_df = df[fields].rename(renamer, axis='columns')
    tsv = renamed_df.to_csv(sep='\t', index=False)
    return tsv

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
    instance_code = store_data.get("instance_code", False)
    # Don't refresh header or table headings if a cell is edited or pasted
    update_data_only = False
    if not instance_code:
        return [], [], "No instance selected"
    instance_dict = app_data.get_instance_by_instance_code(instance_code)
    trigger = dash.callback_context.triggered[0].get("prop_id")
    permissions = app_data.get_permissions(request.headers.get("X-Email"))
    # If we're here because a cell has been edited
    if "cellEdited" in trigger and permissions.get("can_edit_ap"):
        update_data_only = update_result(changed)
    elif "clipboardPasted" in trigger and permissions.get("can_edit_ap") and not instance_dict.get('moderated'):
        lecturer = request.headers.get("X-Email")
        for row in row_data:
            # check student id
            student_id_string = row.get('student_id', False)
            if student_id_string:
                try:
                    student_id = int(student_id_string)
                except ValueError:
                    break
            component_names = set([k.split(":")[0] for k in row.keys() if ":" in k])
            for component_name in component_names:
                new_string_value = row.get(f'{component_name}:value', False)
                if new_string_value:
                    try:
                        new_value = float(new_string_value)
                    except ValueError:
                        break
                    update_data_only = app_data.set_result_by_component_name_instance_code(student_id, new_value, component_name, instance_code, lecturer)
    components_dicts = app_data.get_results_for_instance_code(instance_code)
    if not components_dicts:
        return [], [], "There are no students in this instance yet"
    components_df = pd.DataFrame.from_records(components_dicts, columns=["result_id", "given_name", "family_name", "college_email", "student_id", "name", "value", "capped", "weight", "comment"])
    # Calculate module results from components
    components_df['value'] = pd.to_numeric(components_df['value'], errors='coerce', downcast='integer').round(2)
    components_df.eval("weighted_value = value * weight", inplace=True)
    results_series = components_df.groupby("student_id").sum().eval("total = weighted_value / weight")["total"]
    results_series = results_series.apply(app_data.round_normal)
    # Number duplicate components so we can unstack the dataframe later
    components_df["name"] = components_df["name"] + components_df.groupby(["student_id", "name"]).cumcount().astype(str).replace('0', '')
    components_df = components_df.set_index(["student_id", "given_name", "family_name", "college_email", "name"])[["result_id", "value", "capped", "comment"]]
    pivoted_components_df = components_df.unstack().swaplevel(axis=1).sort_index(axis=1, ascending=[True, False])
    # Columns is still a multiindex
    component_columns = pivoted_components_df.columns.to_flat_index()
    # Component columns of form component:result_id, component:value, component:capped and component:comment
    pivoted_components_df.columns = [":".join(c) for c in component_columns]
    # Join overall results
    pivoted_components_df = pivoted_components_df.join(results_series).reset_index()
    if update_data_only:
        heading = no_update
        columns = no_update
        table_data = pivoted_components_df.sort_values(["family_name", "given_name"]).to_dict(orient='records')
    else:
        heading = f'{instance_code} - {"Moderated" if instance_dict.get("moderated") else "Unmoderated"}'
        columns = build_columns(pivoted_components_df, permissions.get("can_edit_ap") and not instance_dict.get("moderated"))
        table_data = pivoted_components_df.sort_values(["family_name", "given_name"]).to_dict(orient='records')
    return table_data, columns, heading


def update_result(changed):
    column = changed.get("column")
    row = changed.get("row")
    component_name, _ = column.split(":")
    result_id = row.get(f'{component_name}:result_id')
    new_value = row.get(f'{component_name}:value')
    # Validation should happen at table edit level not here
    if type(new_value) == int and (new_value < 0 or new_value > 100):
        return False
    elif new_value == "":
        # psycopg wants None for null
        new_value = None
    new_capped = row.get(f'{component_name}:capped')
    new_comment = row.get(f'{component_name}:comment')
    lecturer = request.headers.get("X-Email")
    success = app_data.update_result_by_id(result_id, new_value, new_capped, new_comment, lecturer)
    return success


def build_columns(pivoted_components_df, editable):
    columns_start = [
       {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
            "widthGrow": 2,
            "frozen": True
        },
       {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
            "widthGrow": 2,
            "frozen":True
        },
        {
            "title": "Total",
            "field": "total",
            "widthGrow": 1,
            "clipboard": False,
            "download": False,
            "frozen": True
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
            "field": "college_email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        }]

    # Build list of component columns for tabulator
    columns_middle = []
    for component, column_type in [c.split(":") for c in pivoted_components_df.columns if ":" in c]:
        if column_type == 'result_id':
            columns_middle.append({"title": "result_id", "field": f'{component}:result_id', "visible": False, "download": False, "clipboard": False})
        elif column_type == 'value':
            columns_middle.append({"title": component,
                                   "field": f'{component}:value',
                                   "editor": "number" if editable else False,
                                   "editorParams": {"max": 100, "min": 0, "step": 1},
                                   "widthGrow": 1})
        elif column_type == 'capped':
            columns_middle.append({"title": "Cap",
                                   "field": f'{component}:capped',
                                   "editor": editable,
                                   "align": "center",
                                   "clipboard": False,
                                   "download": False,
                                   "formatter": "tickCross",
                                   "formatterParams": {"crossElement": False}, "widthGrow": 1})
        elif column_type == 'comment':
            columns_middle.append({"title": "Comment",
                                   "field": f'{component}:comment',
                                   "clipboard": False,
                                   "download": False,
                                   "editor": "textarea" if editable else False})

    return columns_start + columns_middle
