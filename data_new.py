import os
import webbrowser
from threading import Timer

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.graph_objects as go

import dash_bootstrap_components as dbc

# Read and process data
df = pd.read_csv('measures_v2.csv')
# df = df.round(3)  # Round all columns to 3 decimal places
print(df.shape)
#df = df.abs()
df['motor_speed'] = 0.1 * df['motor_speed']  # Scale motor_speed
df['time'] = range(1, len(df) + 1)
# Add calculated parameters
df['output_power'] = df['motor_speed'] * df['torque']  # Output Power
#inp_power = (df['u_d'] * df['i_d'] + df['u_q'] * df['i_q'])
inp_power = (df['u_q']**2 + df['u_d']**2)**0.5 * (df['i_d']**2 + df['i_q']**2)**0.5  # Input Power
df['input_power'] = inp_power
df['efficiency'] = 100*(df['output_power']/(df['input_power']))
df = df[df['efficiency']<100]
#df = df[df['efficiency']>0]

parameters = {'u_q': 'Voltage (V)','u_d': 'Voltage (V)','i_q': 'Current (A)', 'i_d': 'Current (A)',  'torque': "Torque (Nm)",'motor_speed': "RPM",
              'coolant': "Temperature (°C)",  'ambient': "Temperature (°C)",'input_power': "Watt", 'output_power': "Watt",'efficiency':'efficiency'}
              
eda_parameters = {'u_q':'Voltage u_q (V)', 'u_d':'Voltage u_d (V)', 'i_d':'Current i_d (A)', 'i_q':'Current i_q (A)', 'motor_speed':'Motor Speed in RPM','torque':'Torque in Nm'}



# Define the font style for the heading
heading_style = {
    'font-family': "Courier New, monospace",
    'font-size': '56px',
    'text-align': 'center',
    'color': 'white',
    'margin-top': '20px',
    'margin-bottom': '30px'
}



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div([
    html.H1("PMSM Data Visualization", className="text-center", style=heading_style),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Timeseries Graphs', 'value': 'TG'},
            {'label': 'EDA', 'value': 'EDA'}
        ],
        value='TG',
        style={'width': '50%'}
    ),
    html.Div(id='dd-output-container')
])

# Precompute figures
figures = [dcc.Graph(
    id='graph-' + param,
    style={'width': '90%', 'height':'90%', 'margin': '0 auto'},
    figure=go.Figure(
        data=go.Scatter(x=df['time'], y=df[param], mode='lines', name=param),
        layout=go.Layout(
            title={'text': param.capitalize(), 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            xaxis=dict(title='time'),
            yaxis=dict(title=label),
            template='plotly_dark',
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="white")
        )
    )
) for param, label in parameters.items()]

box_plots = [dcc.Graph(
    id='box-' + param,
    style={'width': '90%', 'height':'90%', 'margin': '0 auto'},
    figure=go.Figure(
        data=go.Box(y=df[param], name=param),
        layout=go.Layout(
            title={'text': label, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            template='plotly_dark',
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="white")
        )
    )
) for param, label in eda_parameters.items()]

@app.callback(
    Output('dd-output-container', 'children'),
    [Input('dropdown', 'value')]
)
def update_output(value):
    if value == 'TG':
        return figures
    elif value == 'EDA':
        return box_plots


def open_browser():
    webbrowser.open_new('http://127.0.0.1:1222/')


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run_server(debug=False, use_reloader=False, port=1222)
