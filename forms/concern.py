"""
Conern report form
"""
import dash_core_components as dcc
import dash_html_components as html
import curriculum

layout = [
    html.Form(
        id="form-concern",
        children=[
            dcc.Dropdown(
                id="dropdown-concern-category",
                options=curriculum.concern_categories["options"],
                value=curriculum.concern_categories["default"],
            ),
            dcc.Input(id="input-concern-description", type="text", debounce=False),
            dcc.ConfirmDialog(id="dialog-concern-confirm"),
            html.Div(id="div-concern-message"),
        ],
    )
]
