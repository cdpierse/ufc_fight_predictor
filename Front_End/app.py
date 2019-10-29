import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import os
import sys
import pandas as pd

external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


filedir = os.path.join(
    os.getcwd(), 'Fight_Predictor', 'Data', 'Scraped_Data', 'scraped_fighters.csv')

fighters = pd.read_csv(filedir)


app.layout = html.Div(
    [
        html.Div(
            [
                html.Label('Fighter 1'),
                dcc.Dropdown(options=[
                    {'label': i, 'value': i} for i in fighters.fighter_name.unique()],
                    placeholder='Fighter 1 '
                )


            ], style={'align': 'left'}),
        html.Div(
            [
                html.Label('Fighter 2'),
                dcc.Dropdown(options=[
                    {'label': i, 'value': i} for i in fighters.fighter_name.unique()],
                    placeholder='Fighter 2 '
                )


            ], style={'align': 'right'})

    ], style={'columnCount': 2})


if __name__ == '__main__':
    app.run_server(debug=True)
