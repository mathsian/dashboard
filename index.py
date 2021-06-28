import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
import filters
import nav

app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dbc.Row(children=[
        dbc.Col([
                nav.layout,
            html.Div(id="content")
            ]),
    ]),
    dcc.Store(id="store-data", data={}),
    dcc.Store(id="selected-student-ids", data=[]),
], fluid=True)

# Get all content in the validation layout to avoid callback errors
app.validation_layout = [nav.layout] + [
    page.validation_layout for page in nav.url_map.values()
]

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
