import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard import app
from pages import report, student, subject, top

# Top level container
app.layout = html.Div([
    dcc.Store(id='current-focus', storage_type='memory', data={}),
    html.Div(id='heading-content'),
    dcc.Tabs(id='top-tabs', value='cohort-tab',
             children=[
                 dcc.Tab(value='cohort-tab', label="Cohort"),
                 dcc.Tab(value='team-tab', label="Team"),
                 dcc.Tab(value='subject-tab', label="Subject"),
                 dcc.Tab(value='student-tab', label="Student")
             ]),
    html.Div(id='top-tab-content')
])


@app.callback(Output('top-tab-content', 'children'), [Input('top-tabs', 'value')])
def display_page(tab):
    response = top.layout
    if tab == 'student-tab':
        response = student.layout
    elif tab == 'subject-tab':
        response = subject.layout
    elif tab == 'top-tab':
        response = top.layout
    elif tab == 'team-tab':
        response = top.layout
    return response


if __name__ == '__main__':
    app.run_server(debug=True)
