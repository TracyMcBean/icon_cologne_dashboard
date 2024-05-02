from dash.dependencies import Input, Output
#from app import app  # import the dash app object

from datetime import datetime
import xarray as xr
import pandas as pd
import plotly.graph_objects as go

from .style_functions import style_figure, style_error
from utils.error_utils import var_exists

# This wrapping function is to avoid circular imports
def get_callbacks_vars1d(app, config):
    @app.callback(Output(component_id='intermediate-ds-vars1d', component_property='data'),
                Input(component_id='datepicker', component_property='date'),
                Input(component_id='path', component_property='value'))
    def get_data(seldate, path):
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')
        
        ds = xr.open_dataset(
            path+'/'+ config['paths']['prefix_meteogram'] + seldate + config['paths']['postfix_meteogram']+'.nc')
        
        var_list = ['T2M', 'P_SFC', 'TQV', 'TQC', 'TQI']
        var_list = var_exists(var_list, ds)

        ds_sub1d = ds[var_list]
        df = ds_sub1d.to_dataframe()
        df = df.reset_index(col_fill='time')
        # The data set must be converted to json so that it is stored as binary to be used in other functions
        return df.to_json(date_format='iso', orient='split')

    @app.callback(Output(component_id='line_plot', component_property='figure'),
                Input(component_id='dropdown_vars1d', component_property='value'),
                Input('intermediate-ds-vars1d', 'data'))
    def graph_update_vars1d(dropdown_value, df_json):
        df = pd.read_json(df_json, orient='split')

        # check if the variable is in the dataframe, if not use default error plot
        if dropdown_value not in df.columns:
            fig = go.Figure()
            fig = style_error(fig)
            return fig
        
        fig = go.Figure([go.Scatter(x=df['time'], y=df['{}'.format(dropdown_value)],
            line=dict(color='firebrick', width=3))
            ])
        # apply styling to the figure
        fig = style_figure(fig)

        titles = {
            'T2M': {'yaxis_title': 'K'},
            'P_SFC': {'yaxis_title': 'hPa'},
            'TQV': {'yaxis_title': 'kg m-2'},
            'TQC': {'yaxis_title': 'kg m-2'},
            'TQI': {'yaxis_title': 'kg m-2'}
        }
        if dropdown_value in titles:
            title = titles[dropdown_value]
            fig.update_layout(
            xaxis_title='Time',
            yaxis_title=title['yaxis_title'],
            margin=dict(l=20, r=20, t=20, b=10),  # set the margin values
            height=380  # set the figure height to 300 pixels
            )
        return fig
