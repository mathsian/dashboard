"""
Kudos report form
"""
import dash_core_components as dcc
import dash_html_components as html
import curriculum

layout = [
    html.Div(id="div-kudos-message"),
    html.Form(
        id="form-kudos",
        children=[
            dcc.Dropdown(
                id="dropdown-kudos-value",
                options=curriculum.values_dropdown["options"],
                value=curriculum.values_dropdown["default"],
            ),
            dcc.Dropdown(
                id="dropdown-kudos-points",
                options=curriculum.kudos_points_dropdown["options"],
                value=curriculum.kudos_points_dropdown["default"],
            ),
            dcc.Input(id="input-kudos-description", type="text", debounce=False),
            dcc.ConfirmDialog(id="dialog-kudos-confirm"),
        ],
    ),
]
