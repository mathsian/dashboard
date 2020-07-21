import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from dashboard import app
from pages import student, subject, report, top

# Top level container
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

# Only one callback required. When the url changes, replace the layout
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    response = html.Div([f'404 I guess on {pathname}'])
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
