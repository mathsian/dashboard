import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
import filters
import nav

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Container(
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            dbc.Card(
                                [dbc.CardHeader("data@ada"), dbc.CardBody(nav.layout)]
                            ),
                            html.Br(),
                            dbc.Card(
                                [dbc.CardHeader("Filter"), dbc.CardBody(filters.layout)]
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(id="content"),
                ]
            ),
            fluid=True,
        ),
        dcc.Store(id="store-data", data={}),
    ]
)

# Get all content in the validation layout to avoid callback errors
app.validation_layout = [nav.layout, filters.layout] + [
    page.validation_layout for page in nav.url_map.values()
]


if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
