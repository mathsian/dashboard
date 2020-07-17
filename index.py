import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard import app
from pages import student, subject, top, report

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    response = html.Div(["404 I guess"])
    if pathname == '/pages/student':
        response = student.layout
    elif pathname == '/pages/subject':
        response = subject.layout
    elif pathname == '/pages/top':
        response = top.layout
    elif pathname == '/pages/report':
        response = report.layout
    return response

if __name__ == '__main__':
    app.run_server(debug=True)
