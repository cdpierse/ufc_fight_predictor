import os
import sys
import requests

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from textwrap import dedent as d
from dash.dependencies import Input, Output, State
from flask import jsonify
import json

external_stylesheets = [
    '//cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.css', dbc.themes.COSMO]

filedir = os.path.join('fightPredictor', 'Data',
                       'Scraped_Data', 'scraped_fighters.csv')

fighters = pd.read_csv(filedir)

navbar = dbc.Navbar('UFC Fight Predictor', sticky='top',
                    className='h1', style={'justify': 'center'})

fighter1_dropdown = dcc.Dropdown(id='f1_dropdown', options=[
    {'label': i, 'value': i} for i in fighters.fighter_name.unique()],
    placeholder='Fighter 1 ', style={'height': '30px', 'width': '300px', 'text-align': 'center'},
    value=None)

fighter2_dropdown = dcc.Dropdown(id='f2_dropdown', options=[
    {'label': i, 'value': i} for i in fighters.fighter_name.unique()],
    placeholder='Fighter 2 ', style={'height': '30px', 'width': '300px', 'text-align': 'center'},
    value=None)

predict_button = dbc.Button(
    'Predict', id='predict-button', style={
        'text-align': 'center'},
    className="mr-2", color='primary', block=True, n_clicks=None, active=False)

results = html.Div([dcc.Markdown(d("""
                    **Click to predict winner**. """)),
                    html.Pre(id='click-predict'), ],
                   className='three columns')
body = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(fighter1_dropdown),
                dbc.Col(fighter2_dropdown),

            ],
        ),
        dbc.Col(
            [
                predict_button,
                results
            ],
        )
    ], style={'display': 'inline-flex'}

)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([navbar, body])


@app.callback(Output('click-predict', 'children'),
              [Input('f1_dropdown', 'value'),
               Input('f2_dropdown', 'value'),
               Input('predict-button', 'n_clicks')])
def update_fighters(fighter1, fighter2, n_clicks):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'predict-button.n_clicks':
        if fighter1 is not None and fighter2 is not None:
            fighters = {'fighter1': fighter1, 'fighter2': fighter2}
            message = {'data': fighters}
            r = requests.post(
                "http://localhost:5000/fight-predictor/api/v1.0/predict",json= message)
            
            return f'{r.text}'


if __name__ == '__main__':
    app.run_server(debug=True)
