import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from datetime import date, datetime
import pathlib
import tomli

from callbacks.vars1d_callbacks import get_callbacks_vars1d
from callbacks.precip_callbacks import get_callbacks_precip
from callbacks.time_height_callbacks import get_callbacks_timeheight
from callbacks.hydrometeors_callbacks import get_callbacks_hydrometeors

# Initialize your Dash app
app = dash.Dash(__name__)

config_path = pathlib.Path("./assets/config.toml")
if config_path.exists():
    with config_path.open(mode="rb") as fp:
        config = tomli.load(fp)
else:
    config = {}

bg_color = config['style']['bg_color'] # color for the background of entire page
divider_color = config['style']['divider_color'] # dividers between rows
text_color = config['style']['text_color']    # text color for the entire page

# Here we define the layout of the app
app.layout = html.Div(id='parent', children=[
    
    # make a coloredbanner with a title
    html.Div(children=[
        html.H1(id='H1', children='ICON Cologne Dashboard')
            ], style={'background-color': '#005176', 'color': 'white', 'padding': '10px'}
        ),

    # thin bar with specified color
    html.Div(style={'height': '5px', 'background-color': divider_color}),
    html.Div(children=[
        html.P("Select a date: "),
        dcc.DatePickerSingle(id='datepicker',
                             date=date(2021, 9, 9),
                             display_format='YYYY-MM-DD',
                             max_date_allowed=datetime.today(), 
                             style={'margin-left': '10px'}),
        html.P("Select level range: "),
        html.Div(children=[
            dcc.RangeSlider(id='height_slider', min=30, max=config['data.meteogram']['maxlev_idx'], 
                        step=1, value=[50,config['data.meteogram']['maxlev_idx']],
                        marks=None,
                        tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                                },
                    ),
            ], style={'width': '50%', 'margin-left': '10px'}),
                          # marks={[i: ' {}'.format(i) for i in range(30, 121, 10)]}),
        html.P("Path to data: ", style={'margin-left': '20px'}),
        # for development only use the path to the data on the server
        dcc.Input(id='path', type='text', value=config['paths']['data'],
                   style={'width': '20%', 'margin-left': '10px'}),
    ], style={'text-align': 'left', 'padding': '10px',
            'background-color': '#0077a1', 'color': text_color, 'padding': '10px'}),
    # thin bar with specified color
    html.Div(style={'height': '5px', 'background-color': divider_color}),

    # first row separated into 2 columns
    html.Div(children=[
        # dropdown menu for 1d variables
        html.Div(children=[
            html.H3("1D Variables"),
            html.P("Select variable: "),
            dcc.Dropdown(id='dropdown_vars1d',
                    options=[
                           {'label': '2m Temperature', 'value': 'T2M'},
                           {'label': 'Surface pressure', 'value': 'P_SFC'},
                           {'label': 'IWV', 'value': 'TQV'},
                           {'label': 'LWP', 'value': 'TQC'},
                           {'label': 'IWP', 'value': 'TQI'},
                    ],
                    value='T2M', style={ 'color': '#0077a1'}),
            # add a button to select if logarithmic scale should be used
            dcc.Graph(id='line_plot')            
            ], style={'width': '40%', 'display': 'inline-block', 'margin-right': '4%',
                      'vertical-align': 'top', 'padding': '10px', 'padding-left': '20px'}
                      # the margin creates a gap between the two columns
                      # the vertical-align aligns the bottom of the plot with the bottom of the div
        ),
        # second column plot
        html.Div(children=[
            html.H3("Precipitation"),
            dcc.Graph(id='precip_plot')],
            style={'width': '40%', 'display': 'inline-block',  'margin-left': '4%',
                  'vertical-align': 'top','padding': '10px'}
        ),
    ], style={'color': text_color}),

    # three round dots in the center of the page
    html.Div(children=[
        html.H1("• • •"),
    ], style={'text-align': 'center', 'padding': '10px', 'color': divider_color, 'letter-spacing': '20px'}),

    html.Div(children=[
        html.Div(children=[
            html.H3("Time-height variables"),
            html.P("Select variable: "),
            dcc.Dropdown(id='dropdown_timeheight',
                        options=[
                            {'label': 'Cloud cover', 'value': 'CLC'},
                            {'label': 'Temperature', 'value': 'T'},
                            {'label': 'Density', 'value': 'RHO'},
                            {'label': 'Pressure', 'value': 'P'},
                            {'label': 'Relative humidity', 'value': 'REL_HUM'},
                            {'label': 'Horizontal wind U', 'value': 'U'},
                            {'label': 'horizontal wind V', 'value': 'V'},
                        ],
                        value='CLC', style={ 'color': '#0077a1'}),
        dcc.Graph(id='timeheight_plot'),
        ], style={'width': '40%', 'display': 'inline-block', 'margin-right': '4%',
                  'vertical-align': 'top', 'padding': '5px',
                  'padding-left': '20px'}),

        html.Div(children=[
            html.H3("Hydrometeors"),
            html.P("Select variable: "),
            dcc.Dropdown(id='dropdown_hydrometeors',
                        options=[
                            {'label': 'Specific humidity', 'value': 'QV'},
                            {'label': 'Cloud water mass', 'value': 'QC'},
                            {'label': 'Cloud ice mass', 'value': 'QI'},
                            {'label': 'Rain mass', 'value': 'QR'},
                            {'label': 'Snow mass', 'value': 'QS'},
                            {'label': 'Graupel mass', 'value': 'QG'},
                            {'label': 'Hail mass', 'value': 'QH'},
                            {'label': 'Total hydrometeors mass', 'value': 'total hydrometeors'},
                            {'label': 'Cloud water number conc.', 'value': 'QNC'},
                            {'label': 'Cloud ice number conc.', 'value': 'QNI'},
                            {'label': 'Rain number conc.', 'value': 'QNR'},
                            {'label': 'Snow number conc.', 'value': 'QNS'},
                            {'label': 'Graupel number conc.', 'value': 'QNG'},
                            {'label': 'Hail number conc.', 'value': 'QNH'},
                        ],
                        value='QV', style={ 'color': '#0077a1'}),
            dcc.Graph(id='hydrometeors_plot')
        ], style={'width': '40%', 'display': 'inline-block',  'margin-left': '4%',
                  'padding': '5px', 'vertical-align': 'top'}
        ),
    ]),
    
    # dcc.Store inside the app that stores the intermediate value
    dcc.Store(id='intermediate-ds-vars1d'),
    dcc.Store(id='intermediate-ds-precip'),
    dcc.Store(id='intermediate-ds-timeheight'),
    dcc.Store(id='intermediate-ds-hydrometeors')
], style={'font-family': 'system-ui', 'background-color': bg_color, 'color': text_color})

get_callbacks_vars1d(app, config)
get_callbacks_precip(app, config)
get_callbacks_timeheight(app, config)
get_callbacks_hydrometeors(app, config)


if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run(debug=True)
