import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_table

# Load once outside of any callbacks
df = pd.read_csv("All.csv")

app = dash.Dash(__name__)
server = app.server

# The layout of the dashboard
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='cohort-dropdown',
            options=[
                {'label': 'Cohort 1618', 'value': 1},
                {'label': 'Cohort 1719', 'value': 2},
                {'label': 'Cohort 1820', 'value': 3},
            ],
            value=1),
        html.Div(id='output-container'),
        html.Div([dcc.Graph(id='cohort-graph')]),
        dash_table.DataTable(
            id='cohort-table',
            columns=[
                {"name": c, "id": c} for c in df.columns
            ]),
    ])
])

# A quick callback to make sure the dropdown is working
@app.callback(
    Output('output-container', 'children'),
    [Input('cohort-dropdown', 'value')])
def update_output(value):
    return 'You selected cohort {}'.format(value)

# When the cohort dropdown changes, reload the graph
@app.callback(
    Output('cohort-graph','figure'),
    [Input('cohort-dropdown','value')])
def update_figure(value):
    cohort_data = df[df.Cohort == value]
    return {
        'data': [
            go.Scatter(
            x = cohort_data.GCSE_APS,
            y = cohort_data.AS_Marks,
            mode = 'markers',
            marker = dict(color = cohort_data.GCSE_Maths)
            )
            ],
        'layout': 
            go.Layout(
            title = value,
            yaxis = {"range": [0,240]}
            )
        }
# When the cohort dropdown changes, reload the table
@app.callback(
    Output('cohort-table','data'),
    [Input('cohort-dropdown','value')])
def update_table(value):
    cohort_data = df[df.Cohort == value]
    return cohort_data.to_dict("rows")

if __name__ == '__main__':
    app.run_server(debug=True)

