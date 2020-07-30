"""
Kudos report form
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dashboard import app, save_docs
import curriculum
import datetime

layout = [
    html.Form(id='kudos-form',
                   children=[
                       dcc.Dropdown(id='kudos-value-dropdown',
                                    options=curriculum.values['options'],
                                    value=curriculum.values['default']),
                       dcc.Dropdown(id='kudos-points-dropdown',
                                    options=curriculum.kudos_points['options'],
                                    value=curriculum.kudos_points['default']
                                    ),
                       dcc.Input(id='kudos-input-description', type='text', debounce=False),
                       dcc.ConfirmDialog(id='kudos-confirm-dialog'),
                       html.Div(id='kudos-successful')
                   ])]


@app.callback(
    [Output('kudos-confirm-dialog', 'message'),
     Output('kudos-confirm-dialog', 'displayed')
    ],
    [Input('kudos-input-description', 'n_submit')],
    [State('kudos-input-description', 'value'),
     State('kudos-value-dropdown', 'value'),
     State('kudos-points-dropdown', 'value')]
)
def confirm_kudos(n_submit, description, value, points):
    if n_submit:
        msg = f'Award {points} {value} kudos for {description}?'
        return msg, True
    else:
        return "", False


@app.callback(
    Output('kudos-successful', 'children'),
    [Input('kudos-confirm-dialog', 'submit_n_clicks')],
    [State('kudos-input-description', 'value'),
     State('kudos-value-dropdown', 'value'),
     State('kudos-points-dropdown', 'value'),
     State('current-student', 'data')]
)
def submit_kudos(clicks, description, value, points, student_id):
    if clicks and student_id:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        doc = {'type': 'kudos',
               'student_id': student_id,
               'ada_value': value,
               'points': points,
               'date': date}
        result = save_docs([doc])
        return str(result)
    else:
        return "Not submitted"
