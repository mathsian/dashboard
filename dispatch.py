from dash.dependencies import Input, Output 


def get_dropdown_visibility(tab):
    tab_dict = {
        "tab-main-cohort": (True, True, True),
        "tab-main-team": (False, True, True),
        "tab-main-subject": (True, False, False),
        "tab-main-student": (False, True, True)
    }
    return tab_dict.get(tab)


def register_callbacks(app):
    @app.callback(
        [
            Output("div-dropdown-team", "hidden"),
            Output("div-dropdown-subject", "hidden"),
            Output("div-dropdown-assessment", "hidden"),
        ],
        [Input("tabs-main", "value")],
    )
    def dispatch_hide_dropdowns(tabs_main_value):
        return *get_dropdown_visibility(tabs_main_value),
