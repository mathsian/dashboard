import dash_tabulator
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from app import app
import app_data
from dash_extensions.javascript import Namespace
from dash.exceptions import PreventUpdate

ns = Namespace("myNameSpace", "tabulator")

layout = dbc.Accordion(
    id={
        "type": "accordion",
        "section": "apprenticeships",
        "page": "info",
        "tab": "upcoming",
    }
)


@app.callback(
    Output({
        "type": "accordion",
        "section": "apprenticeships",
        "page": "info",
        "tab": "upcoming",
    }, "children"), [
        Input(
            {
                "type": "button",
                "section": "apprenticeships",
                "page": "info",
                "name": "update"
            }, "n_clicks")
    ])
def update_upcoming_table(n_clicks):
    upcoming_df = pd.DataFrame.from_records(app_data.get_upcoming_class_lists())
    if not len(upcoming_df):
        raise PreventUpdate
    accordion_items = []
    upcoming_codes = upcoming_df.groupby(['code', 'start_date'], as_index=False).size().sort_values(['start_date', 'code'], ascending=[False, True]).set_index('code').index
    upcoming_df.set_index('code', inplace=True)
    for code in upcoming_codes:
        accordion_title = code
        # accordion_content = dbc.Table.from_dataframe(upcoming_df.loc[[code], :])
        accordion_content = create_class_table(upcoming_df.loc[[code], :])
        accordion_items.append(dbc.AccordionItem(children=accordion_content, title=accordion_title))
    return accordion_items


def create_class_table(class_df):
    class_table = dash_tabulator.DashTabulator(
        theme='bootstrap/tabulator_bootstrap4',
        options={
            "resizableColumns": False,
            "clipboard": "copy",
            "clipboardCopySelector": "table",
            "clipboardCopyConfig": {"formatCells": False},
        },
        columns=[{
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
            "field": "email",
        }, {
            "title": "Employer",
            "field": "employer"
        }, {
            "title": "Cohort",
            "field": "cohort"
        }],
        data=class_df.to_dict(orient='records'))
    return class_table 

